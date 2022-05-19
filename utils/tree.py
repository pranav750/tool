# Importing the required libraries
import os

# For creating Link Tree
from anytree import Node, RenderTree

# Generate Link tree in results/link_tree.txt
def link_tree_formation(crawled_links):
    print("Generating Link Tree...")
    root = None
    tree_dict = dict()

    # Create tree nodes of all the links and store in tree dictionary
    for result in crawled_links:
        node = Node(result['link'])
        tree_dict[result['link']] = node
    
    # Setting up the parent nodes and root node
    for result in crawled_links:
        if result['parent_link'] == '':
            root = tree_dict[result['link']]
        else:
            tree_dict[result['link']].parent = tree_dict[result['parent_link']]

    # Putting link tree in results/link_tree.txt
    link_tree = open(os.path.join(os.path.dirname( __file__ ), '..', 'results', 'link_tree.txt'), 'w', encoding = 'utf-8')
    link_tree.flush()
        
    for pre, fill, node in RenderTree(root):
        link_tree.write("%s%s" % (pre, node.name))
        link_tree.write("\n")