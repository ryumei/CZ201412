#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  summary_redmines.py: Sample
#  Created by NAKAJIMA Takaaki on Nov 25, 2014.
#
from redmine import Redmine
import json
from jinja2 import Template, Environment, FileSystemLoader

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
        for node in item_map.values():
            if (node.has_parent and (node.item.parent.id in item_map)):
                parent_id = node.item.parent.id
                item_map[parent_id].add_child(node)
            else:
                item_root.append(node)
        item_map.clear()
        return item_root

class IssueNode(Node):
    def execute(self, family):
        print(self.item.id)

class ProjectNode(Node):
    env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
    issue_tmpl = env.get_template('issue.tmpl.html')
    project_tmpl = env.get_template('project.tmpl.html')
    
    def url(self):
        return 'REDMINE_BASE/projects/' + str(self.item.id)

    def deduplicate_issues(self, issues):
        project_id = self.item.id
        deduplicated = []
        for issue in issues:
            if (issue.project.id == project_id):
                deduplicated.append(issue)
        return deduplicated

    def execute(self, family):
        issues = redmine.issue.all(project_id=self.item.id)
        issues = self.deduplicate_issues(issues)
        
        project_html = self.project_tmpl.render({'name':' / '.join(family),
                                                 'url':self.url(),
                                                 'issues_size':len(issues)})
        print project_html.encode('utf-8')
        print("Project:%s has %d issues" % 
                ('/'.join(family), len(issues)))
        
        issue_root = IssueNode.item_root(issues)
        
        issues_html = self.issue_tmpl.render({'issues':issue_root})
        print issues_html.encode('utf-8')
        
        # [NOT USED] traverse issue tree
        #for node in issue_root:
        #    node.execute([])

# ----------------------------------------------------------------------

# Load config
raw_conf_data = open('./conf.json')
conf = json.load(raw_conf_data)
raw_conf_data.close()

print 'Content-Type: text/html; charset=utf-8\n'

# Main routine
for key in conf:
    site = conf[key]
    redmine = Redmine(site[u'site'], key=site[u'key'])
    
    projects = redmine.project.all()
    print("%s has %d projects" % (key, len(projects)))

    project_root = ProjectNode.item_root(projects)
    for node in project_root:
        node.trace()
    
    #env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
    #tmpl = env.get_template('sample.tmpl.html')
    
    #html = tmpl.render({'title':u'サンプル', 'projects':projects})
    #print "Content-Type: text/html; charset=utf-8\n"
    #print html.encode('utf08')
