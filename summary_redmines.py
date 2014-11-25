#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  summary_redmines.py: Sample
#  Created by NAKAJIMA Takaaki on Nov 25, 2014.
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

    def execute(self, family=None):
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
    def str(self):
        message = """Issue:[{id}] {subject} 
作成者: {author}
担当者: {assigned_to}
作成日: {created_on}
開始日: {start_date}
更新日: {updated_on}
期日: {due_date}
状態: {status}

"""
        issue = self.item
        return message.format(id=issue.id,
                subject=issue.subject,
                author=issue.author,
                assigned_to=issue.assigned_to,
                created_on=issue.created_on,
                start_date=issue.start_date,
                updated_on=issue.updated_on,
                due_date=issue.due_date,
                status=issue.status.name)

    def execute(self, family):
        print(self.str())

class ProjectNode(Node):
    def execute(self, family):
        issues = redmine.issue.all(project_id=self.item.id)
        print("Project:%s has %d issues" % 
                ('/'.join(family), len(issues)))

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
    
