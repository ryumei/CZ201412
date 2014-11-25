#! python
# -*- coding: utf-8 -*-
#
#  Created by NAKAJIMA Takaaki on Nov 25, 2014.
#  See also
#  - http://python-redmine.readthedocs.org/index.html
#  - http://qiita.com/mima_ita/items/1a939db423d8ee295c85
#
from redmine import Redmine
import json

# ----------------------------------------------------------------------

class Node:
    def __init__(self, item):
        self.item = item
        self.children = []
        self.has_parent = hasattr(item, u'parent')
    
    def add_child(self, child):
        self.children.append(child)
    
    def trace(self, family=None):
        family = [] if family is None else family
        family.append(self.item.name)
        
        self.execute(family)
        
        if len(self.children) > 0:
            for child in self.children:
                child.trace(family)
        family.pop()

    def execute(self, family):
        print("%s has %d children" % ('/'.join(family), len(self.children)))

    @classmethod
    def item_root(cls, items):
        item_map = {}
        for item in items:
            item_map[item.id] = cls(item)
        
        item_root = []
        for Node in item_map.values():
            if (Node.has_parent and (Node.item.parent.id in item_map)):
                parent_id = Node.item.parent.id
                item_map[parent_id].add_child(Node)
            else:
                item_root.append(Node)
        item_map.clear()
        return item_root

class IssueNode(Node):
    def execute(self, family):
        print("Issue:[%d] %s" % (self.item.id, self.item.subject))

class ProjectNode(Node):
    def execute(self, family):
        print("Project:%s has %d children" % ('/'.join(family), len(self.children)))
        issues = redmine.issue.all(project_id=self.item.id)
        print("Project:%s has %d issues" % ('/'.join(family), len(issues)))

        issue_root = IssueNode.item_root(issues)
        for node in issue_root:
            node.execute([])

# ----------------------------------------------------------------------

# Load config
raw_conf_data = open('./conf.json')
conf = json.load(raw_conf_data)
raw_conf_data.close()

# Main routine
for key in conf:
    site = conf[key]
    redmine = Redmine(site[u'site'], key=site[u'key'])
    
    projects = redmine.project.all()
    print("%s has %d projects" % (key, len(projects)))

    project_root = ProjectNode.item_root(projects)
    for Node in project_root:
        Node.trace()
    
