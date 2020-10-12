# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_dingding
from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'lcfevr'
    author_url = 'https://github.com/lcfevr/sentry-dingding'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/lcfevr/sentry-dingding'),
        ('Bug Tracker', 'https://github.com/lcfevr/sentry-dingding/issues'),
        ('README', 'https://github.com/lcfevr/sentry-dingding/blob/master/README.md'),
    ]

    slug = 'DingDing'
    title = 'DingDing'
    conf_key = slug
    conf_title = title
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        send_url = DingTalk_API.format(token=access_token)
        title = u"New alert from {}".format(event.project.slug)


        response = requests.get(
            url="http://web-middle.ruibogyl.work/sentry/getDingDingAssignee",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                url: event.url
            })
          ).json()



        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": u"#### {title} \n > {message} [href]({url}) @{phone}".format(
                    title=title,
                    message=event.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.id),
                    phone=response['phone']
                ),

            },
            "at": {
              "atMobiles": [
                  response['phone']
              ],
              "isAtAll": false
          }
        }



        requests.post(
            url=send_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8")
        )
