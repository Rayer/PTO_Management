# Slack PTO Management APP

## Overview

An app for Slack PTO Management. PTOs can be applied in Slack and will be shown in destinated google calendar.

## Commands and Endpoints

- `/pto_apply` It will apply a PTO entry. Format is `/pto_apply name description start end`
	- Due to system limitation, description can be only a word. We usually uses *PTO* *WFH* most.
	- **start** is mandatory, if **end** is not specified, PTO will be made for 1 day.
	- Endpoint is `http://node.rayer.idv.tw:1200/pto/slack/apply`
- `/pto_calendar` Show link to google calendar which shows everyone's PTO.
	- Endpoint is `http://node.rayer.idv.tw:1200/pto/slack/cal`

## Server App

###Deployment

Slack command is fixed to `http://node.rayer.idv.tw:1200` as host and port, so it need to fit this requirement.


