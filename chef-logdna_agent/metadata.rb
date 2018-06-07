name             'logdna_agent'
maintainer       'Toby Sullivan'
maintainer_email 'toby.sullivan@teespring.com'
license          'All rights reserved'
description      'Installs/Configures logdna-agent'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          '0.1.0'

recipe 'logdna_agent::default', 'Installs the LogDNA host agent.'

depends 'apt'
