#
# Cookbook Name:: logdna_agent
# Recipe:: default
#
# Copyright 2016, Toby Sullivan
#
# All rights reserved
#

apt_repository 'logdna' do
  uri        'http://repo.logdna.com'
  components ['stable', 'main']
  distribution nil
  key 'https://s3.amazonaws.com/repo.logdna.com/logdna.gpg'
  action     :add
end

execute 'run logdna-agent' do
  command "logdna-agent -k #{node['logdna_agent']['api_key']}"
  action  :nothing
end

apt_package 'logdna-agent' do
  action   :install
  notifies :run, 'execute[run logdna-agent]', :immediately
end

node['logdna_agent']['log_directories'].each do |dir|
  execute "add #{dir} to logdna-agent" do
    command "logdna-agent -d #{dir}"
  end
end

unless node['logdna_agent']['tags'].nil? || node['logdna_agent']['tags'].empty?
  execute "add tags to logdna-agent" do
    command "logdna-agent -t #{node['logdna_agent']['tags']}"
  end
end

execute 'add logdna-agent to defaults' do
  command 'update-rc.d logdna-agent defaults'
  action  :run
end

service 'logdna-agent' do
  action :start
end
