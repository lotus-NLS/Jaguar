## Overview
The Lotus framework facilitates interaction with the computer and the internet through natural language.
For more information see the "Wiki" section on the [Project management page](https://furtive-point-c71.notion.site/GPT-pyWrite-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4).

<p align="center">
  <img src="https://github.com/Somerandomguy10111/webapp/blob/master/assets/images/logo.jpg" alt="Logo" width="200">
  <br>
  <em> Nelumbo Nucifera the most widely known Lotus Flower</em>
</p>

## Setup and usage for Ubuntu 22.04

This is still in flux, [TODO] later

Requires chrome installation. For can use below ansible playbook:

```
- name: Install Google Chrome
  hosts: localhost
  become: yes
  tasks:
    - name: Download Google Chrome .deb package
      get_url:
        url: "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
        dest: "/tmp/google-chrome-stable_current_amd64.deb"

    - name: Install Google Chrome
      apt:
        deb: "/tmp/google-chrome-stable_current_amd64.deb"

    - name: Ensure Google Chrome is installed
      command: google-chrome --version
      register: chrome_version
      changed_when: false

    - name: Display Chrome version
      debug:
        msg: "{{ chrome_version.stdout }}"
```