#! /usr/bin/env python2


from setuptools import setup


setup(
    name='aawiki',
    version='0.1',
    author='The active archives contributors',
    author_email='alexandre@stdin.fr',
    description=('Active Archives inverts the paradigm of uploading resources',
        'into a centralized server and instead allows resources to remain',
        '"active", in-place and online. Caching and proxy functionality allow',
        'light-weight) copies of resources to be manipulated and preserved',
        'even, as the original sources change or become (temporarily)',
        'unavailable.'),
    url='http://activearchives.org/',
    packages=['aawiki', 'aawiki.mdx', 'aawiki.management', 'aawiki.templatetags'],
    include_package_data = True,
    dependency_links=[
        'git+git://git.constantvzw.org/aa.core2.git#egg=aacore-0.1',
        'git+git://git.constantvzw.org/aa.rdfutils.git#egg=rdfutils-0.1',
    ],
    install_requires=[
        'django>=1.4,<1.5',
        'django-tastypie',
        'pygit2',
        'html5lib',
        'lxml',
        'feedparser',
        'html5tidy',
        'Markdown==2.1.0',
        'mdx-cite==1.0',
        'mdx-del-ins==1.0',
        'mdx-outline==1.02.1',
        'mdx-semanticdata==1.1',
        'mdx-semanticwikilinks==1.1.1',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Markup'
    ]
)
