#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  summary_redmines.py: Sample
#  Created by NAKAJIMA Takaaki on Nov 25, 2014.
#
import json
from redmine import Redmine
from jinja2 import Environment, FileSystemLoader
import datetime 
from datetime import datetime 

today = datetime.now().date()

# ----------------------------------------------------------------------

class Node(object):
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
    def item_root(cls, items, url):
        item_map = {}
        for item in items:
            item_map[item.id] = cls(item, url)
        
        item_root = []
        for node in item_map.values():
            if (node.has_parent and (node.item.parent.id in item_map)):
                parent_id = node.item.parent.id
                item_map[parent_id].add_child(node)
            else:
                item_root.append(node)
        item_map.clear()
        return item_root

datetime_format = '%Y/%m/%d'

class IssueNode(Node):
        
    def __init__(self, item, site_url):
        global today, datetime_format
        
        super(IssueNode, self).__init__(item)
        self.url = site_url + 'issues/' + str(self.item.id)
        
        # 期日のチェック
        if hasattr(item, 'due_date'):
            self.due_date = item.due_date
            due_date = item.due_date
            # due_date = datetime.strptime(item.due_date, datetime_format)
            if due_date <= today:
                self.due_date_status = 0
            else:
                self.due_date_status = 2
        else:
            self.due_date = u'未設定'
            self.due_date_status = 1
        
        # 担当者のチェック
        if hasattr(item, 'assigned_to'):
            self.assigned_to_status = 0
            self.assigned_to = self.item.assigned_to.name
        else:
            self.assigned_to_status = 1
            self.assigned_to = u'担当者なし'
        
        if item.status.id in [ 2, 3 ]: # checking or committed
            self.status_status = True
        else:
            if self.due_date_status > 0 or self.assigned_to_status > 0:
                self.status_status = False
            else:
                self.status_status = True
        
    def execute(self, family):
        print("%d %s %s" % (self.item.id, self.item.subject))
        return self.item.id

class ProjectNode(Node):
    env = Environment(loader=FileSystemLoader('./template', encoding='utf-8'))
    issue_tmpl = env.get_template('issue.tmpl.html')
    project_tmpl = env.get_template('project.tmpl.html')
    
    def __init__(self, item, site_url):
        super(ProjectNode, self).__init__(item)
        self.site_url = site_url
        self.url = site_url + 'projects/' + str(self.item.id)

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
                                                 'url':self.url,
                                                 'issues_size':len(issues)})
        print(project_html)

        if (len(issues) < 1):
            return
        
        issue_root = IssueNode.item_root(issues, self.site_url)
        issues_html = self.issue_tmpl.render({'issues':issue_root})

        print(issues_html)

# ----------------------------------------------------------------------

# Load config
raw_conf_data = open('./conf.json')
conf = json.load(raw_conf_data)
raw_conf_data.close()

env = Environment(loader=FileSystemLoader('./template', encoding='utf-8'))
header_tmpl = env.get_template('header.tmpl.html')

print(header_tmpl.render({'title':u'Redmine まとめ',
                          'generated_on':str(today)}))

site_tmpl = env.get_template('site.tmpl.html')

# Main routine
for key in conf:
    site = conf[key]
    site_url= site['site']
    redmine = Redmine(site_url, key=site[u'key'])
    
    print(site_tmpl.render({'name':key, 'url':site_url}))

    projects = redmine.project.all()
    
    project_root = ProjectNode.item_root(projects, site_url)
    for node in project_root:
        node.trace()

footer_tmpl = env.get_template('footer.tmpl.html')
print(footer_tmpl.render())


