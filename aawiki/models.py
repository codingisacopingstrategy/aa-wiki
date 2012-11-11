"""
Implements active archives models
"""


import codecs
import os
import os.path
from git import Repo, NoSuchPathError
from django.db import models
from aacore.sniffers import AAResource
import aawiki.utils
from aawiki.settings import GIT_DIR
from diff_match_patch import diff_match_patch
from aawiki.mdx import get_markdown


class Page(models.Model):
    """ Represents a wiki page. 
    
    Acts like a proxy to access to the associated GIT repository but caches the
    last revision of a page for convenience.
    
    """
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_diff_url(self):
        return ("aa-page-diff", (), {'slug': aawiki.utils.wikify(self.name)})

    @models.permalink
    def get_history_url(self):
        return ("aa-page-history", (), {'slug': aawiki.utils.wikify(self.name)})

    @models.permalink
    def get_edit_url(self):
        return ("aa-page-edit", (), {'slug': aawiki.utils.wikify(self.name)})

    @models.permalink
    def get_absolute_url(self):
        return ("aa-page-detail", (), {'slug': aawiki.utils.wikify(self.name)})

    @property
    def slug(self):
        """
        Returns the wikified name of the page.
        """
        return aawiki.utils.wikify(self.name)

    def get_repository(self):
        try:
            repo = Repo(GIT_DIR)
        except NoSuchPathError:
            repo = Repo.init(GIT_DIR)
            #repo = Repo.init(GIT_DIR, bare="True")
        return repo

    def iter_commits(self):
        repo = self.get_repository()
        return repo.iter_commits(paths=self.slug)

    def commit(self, amend=False, message="No message", author="Anonymous <anonymous@127.0.0.1>", is_minor=False):
        """
        Commits page content and saves it it in the database.
        """
        # Makes sure the content ends with a newline
        if self.content[-1] != "\n":
            self.content += "\n"

        repo = self.get_repository()

        # Writes content to the CONTENT file
        path = os.path.join(GIT_DIR, self.slug)
        f = codecs.open(path, "w", "utf-8")
        f.write(self.content)
        f.close()

        # Adds the newly creates files and commits
        #repo.index.add([self.slug,])
        repo.git.add([self.slug,])
        repo.git.commit(amend=amend, message=message, author=author)

        # Add the commit metadata in a git note, formatted as
        # a .ini config file
    # THIS SEEMS TO CAUSE AN ERROR:  git: 'notes' is not a git-command. See 'git --help' in git 1.5.6.5 on debian at least
#        config = ConfigParser()
#        config.add_section('metadata')
#        config.set('metadata', 'is_minor', is_minor)

#        output = cStringIO.StringIO()
#        config.write(output)
#        repo.git.notes(["add", "--message=%s" % output.getvalue()], ref="metadata")
        self.save()
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        print(current_site.domain)
        print("reindexing page %s" % self.name)
        AAResource("http://localhost:8000" + self.get_absolute_url()).index()

    def get_commit(self, rev="HEAD"):
        """
        Returns the commit object at a given revision
        """
        repo = self.get_repository()
        return repo.commit(rev)

    def read(self, rev="HEAD"):
        """
        Returns the page content at a given revision
        """
        repo = self.get_repository()
        commit = repo.commit(rev)
        return u"%s" % commit.tree[self.slug].data_stream.read().decode('utf-8')

    def diff(self, c1, c2):
        """
        Compares two revisions
        """
        def diff_prettyXhtml(self, diffs):
            """
            Extends google's diff_patch_match
            Similar to diff_prettyHtml but returns an XHTML valid code
            """
            html = []
            i = 0
            for (op, data) in diffs:
                text = (data.replace("&", "&amp;").replace("<", "&lt;")
                         .replace(">", "&gt;").replace("\n", "<br />"))
                if op == self.DIFF_INSERT:
                    html.append('<ins class="added" title="i=%i">%s</ins>' % (i, text))
                elif op == self.DIFF_DELETE:
                    html.append('<del class="deleted" title="i=%i">%s</del>' % (i, text))
                elif op == self.DIFF_EQUAL:
                    html.append('<span class="equal" title="i=%i">%s</span>' % (i, text))
                if op != self.DIFF_DELETE:
                    i += len(data)
            return "".join(html)

        repo = self.get_repository()
        commit_1 = repo.commit(c1)
        commit_2 = repo.commit(c2)
        f1 = u"%s" % commit_1.tree[self.slug].data_stream.read().decode('utf-8')
        f2 = u"%s" % commit_2.tree[self.slug].data_stream.read().decode('utf-8')
        f1 = f1.encode('utf-8')
        f2 = f2.encode('utf-8')
        ui = diff_match_patch()
        diff = ui.diff_main(f1, f2)
        ui.diff_cleanupSemantic(diff)
        return diff_prettyXhtml(ui, diff)
