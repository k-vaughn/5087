from rdflib import Graph, RDF, RDFS, OWL, XSD
from graphviz import Digraph
import os

# Ensure output directory exists
os.makedirs("docs/diagrams", exist_ok=True)

# Load TTL ontology
g = Graph()
g.parse("transportnetwork.ttl", format="turtle")

# Namespaces
ns = "https://isotc204.org/25965/transport/transportnetwork#"
skos_ns = "http://www.w3.org/2004/02/skos/core#"

# Custom prefixes
prefixes = {
    "https://isotc204.org/25965/transport/transportnetwork#": "",
    "https://www.opengis.net/ont/geosparql#": "geo:",
    "https://www.w3.org/2006/time#": "time:",
    "https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/code#": "code:",
    "https://standards.iso.org/iso-iec/5087/-1/ed-1/en/ontology/GenericProperties#": "genProp:",
    "https://standards.iso.org/iso-iec/5087/-1/ed-1/en/ontology/Mereology#": "partwhole:",
    "https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/transinfras#": "transinfras:",
    "https://isotc204.org/25965/transport/travelcorridor#": "travelcorridor:",
    "http://www.w3.org/2004/02/skos/core#": "skos:",
    "http://www.w3.org/2001/XMLSchema#": "xsd:",
}

def get_qname(uri):
    str_uri = str(uri)
    for base, pref in prefixes.items():
        if str_uri.startswith(base):
            return pref + str_uri[len(base):]
    return str_uri

def get_id(qname):
    if ':' in qname:
        prefix, local = qname.split(':', 1)
        return prefix + '_' + local
    else:
        return qname

def get_all_class_superclasses(cls, g):
    direct_supers = set()
    for super_cls in g.objects(cls, RDFS.subClassOf):
        if (super_cls, RDF.type, OWL.Class) in g or str(super_cls).startswith(ns):
            direct_supers.add(super_cls)
    all_supers = set(direct_supers)
    for sup in direct_supers:
        all_supers.update(get_all_class_superclasses(sup, g))
    return all_supers

# Extract classes
classes = set(g.subjects(RDF.type, OWL.Class)) - {OWL.Thing}

processed_count = 0
errors = []

for cls in classes:
    # Extract class name
    cls_str = str(cls)
    if cls_str.startswith(ns):
        cls_name = get_qname(cls)
        cls_id = get_id(cls_name)
    else:
        continue  # Skip non-local classes

    try:
        print(f"Processing class: {cls_name}")

        # Initialize Graphviz diagram
        dot = Digraph(
            comment=f"Diagram for {cls_name}",
            format="svg",
            graph_attr={"overlap": "false", "splines": "true"},
            node_attr={"shape": "record", "fontsize": "12", "fontname": "Arial"},
            edge_attr={"fontsize": "10", "fontname": "Arial"}
        )

        # Collect superclasses
        superclasses = set()
        for super_cls in g.objects(cls, RDFS.subClassOf):
            if (super_cls, RDF.type, OWL.Class) in g or str(super_cls).startswith(ns):
                superclasses.add(get_qname(super_cls))

        # Collect data properties
        data_props = []
        for restriction in g.objects(cls, RDFS.subClassOf):
            if (restriction, RDF.type, OWL.Restriction) in g:
                prop = g.value(restriction, OWL.onProperty)
                if prop and (prop, RDF.type, OWL.DatatypeProperty) in g:
                    range_type = g.value(prop, RDFS.range) or XSD.string
                    qualified_card = g.value(restriction, OWL.qualifiedCardinality)
                    min_qualified_card = g.value(restriction, OWL.minQualifiedCardinality)
                    max_qualified_card = g.value(restriction, OWL.maxQualifiedCardinality)
                    if qualified_card:
                        card_str = f" [{qualified_card}]"
                    elif min_qualified_card and max_qualified_card:
                        card_str = f" [{min_qualified_card}..{max_qualified_card}]"
                    elif min_qualified_card:
                        card_str = f" [{min_qualified_card}..*]"
                    elif max_qualified_card:
                        card_str = f" [0..{max_qualified_card}]"
                    else:
                        card_str = ""
                    prop_name = get_qname(prop)
                    range_name = get_qname(range_type).split(":")[-1]
                    data_props.append(f"{prop_name}: {range_name}{card_str}")

        attributes = "\\n".join(data_props) if data_props else ""

        # Collect other classes for cluster_others
        other_classes = set()

        # Create main cluster
        with dot.subgraph(name='cluster_main') as main_cluster:
            main_cluster.attr(style='invis', rankdir='TB')
            # Add superclass nodes
            for sup in sorted(superclasses):
                sup_id = get_id(sup)
                main_cluster.node(sup_id, label=sup)
            # Add main node with rank=max
            with main_cluster.subgraph() as s:
                s.attr(rank='max')
                s.node(cls_id, f"{{{cls_name}|{attributes}}}")
            # Add generalization edges
            for sup in sorted(superclasses):
                sup_id = get_id(sup)
                main_cluster.edge(cls_id, sup_id, arrowhead="onormal", style="solid")

        all_supers = get_all_class_superclasses(cls, g)

        # Process object property restrictions
        for restriction in g.objects(cls, RDFS.subClassOf):
            if (restriction, RDF.type, OWL.Restriction) in g:
                prop = g.value(restriction, OWL.onProperty)
                if prop and (prop, RDF.type, OWL.ObjectProperty) in g:
                    prop_name = get_qname(prop)

                    is_inherited = any(
                        any(
                            g.value(rest, OWL.onProperty) == prop
                            for rest in g.objects(sup, RDFS.subClassOf)
                            if (rest, RDF.type, OWL.Restriction) in g
                        )
                        for sup in all_supers
                    )
                    style = "dashed" if is_inherited else "solid"

                    # Handle cardinalities
                    qualified_card = g.value(restriction, OWL.qualifiedCardinality)
                    min_qualified_card = g.value(restriction, OWL.minQualifiedCardinality)
                    max_qualified_card = g.value(restriction, OWL.maxQualifiedCardinality)
                    on_class = g.value(restriction, OWL.onClass)
                    if (qualified_card or min_qualified_card or max_qualified_card) and on_class:
                        target_qname = get_qname(on_class)
                        other_classes.add(target_qname)
                        target_id = get_id(target_qname)
                        if qualified_card:
                            label = f"«qualifiedCardinality»\n{qualified_card}\nonProperty: {prop_name}"
                        elif min_qualified_card and max_qualified_card:
                            label = f"«cardinality»\n{min_qualified_card}..{max_qualified_card}\nonProperty: {prop_name}"
                        elif min_qualified_card:
                            label = f"«minQualifiedCardinality»\n{min_qualified_card}\nonProperty: {prop_name}"
                        elif max_qualified_card:
                            label = f"«maxQualifiedCardinality»\n{max_qualified_card}\nonProperty: {prop_name}"
                        dot.edge(f"{cls_id}:s", target_id, label=label, style=style, arrowhead="normal")

                    # Handle universal (allValuesFrom -> only)
                    all_values_from = g.value(restriction, OWL.allValuesFrom)
                    if all_values_from:
                        target = all_values_from
                        union_collection = g.value(target, OWL.unionOf)
                        if union_collection and union_collection != RDF.nil:
                            members = []
                            current = union_collection
                            while current != RDF.nil:
                                first = g.value(current, RDF.first)
                                if first:
                                    members.append(get_qname(first))
                                current = g.value(current, RDF.rest)
                            if members:
                                members.sort()
                                union_label = "«unionOf»\\n[" + " or ".join(members) + "]"
                                union_id = "Union"
                                dot.node(union_id, union_label, shape="ellipse", fillcolor="lightyellow")
                                for member in members:
                                    other_classes.add(member)
                                    m_id = get_id(member)
                                    dot.edge(union_id, m_id, style="dotted", label="member", arrowhead="normal")
                                label = f"«only» onProperty:\n{prop_name}"
                                dot.edge(f"{cls_id}:s", union_id, label=label, style=style, arrowhead="normal")
                        else:
                            target_qname = get_qname(target)
                            if target_qname != cls_name:
                                other_classes.add(target_qname)
                                target_id = get_id(target_qname)
                                label = f"«only» onProperty:\n{prop_name}"
                                dot.edge(f"{cls_id}:s", target_id, label=label, style=style, arrowhead="normal")
                            else:
                                # reflexive
                                dot.edge(f"{cls_id}:e", cls_id, label=prop_name, style=style)

                    # Handle existential (someValuesFrom)
                    some_values_from = g.value(restriction, OWL.someValuesFrom)
                    if some_values_from:
                        target = some_values_from
                        target_qname = get_qname(target)
                        if target_qname != cls_name:
                            other_classes.add(target_qname)
                            target_id = get_id(target_qname)
                            label = f"«some» onProperty:\n{prop_name}"
                            dot.edge(f"{cls_id}:s", target_id, label=label, style=style, arrowhead="normal")
                        else:
                            # reflexive
                            dot.edge(f"{cls_id}:e", cls_id, label=prop_name, style=style)

        # Create others cluster with collected classes
        with dot.subgraph(name='cluster_others') as others_cluster:
            others_cluster.attr(style='invis')
            for target in sorted(other_classes):
                target_id = get_id(target)
                others_cluster.node(target_id, label=target)

        # Save DOT file and render SVG
        dot_file = f"diagrams/{cls_name}.dot"
        stem = f"diagrams/{cls_name}"
        dot.save(dot_file)
        dot.render(stem, cleanup=False)
        # Render PNG
        dot.render(stem, format='png', cleanup=False)

        processed_count += 1

    except Exception as e:
        errors.append(f"Error processing {cls_name}: {str(e)}")

print(f"Total processed classes: {processed_count}")
if errors:
    print("Errors occurred:")
    for err in errors:
        print(err)
