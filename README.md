# Slack PTO Management APP

## Overview

An app for Slack PTO Management. PTOs can be applied in Slack and will be shown in destinated google calendar.

## `client_secret.json`

This application requires client secret, please contact project owner, or you can issue one [here](https://console.developers.google.com/apis/dashboard?project=u2ber-203314).

Require permission and APIs are Google Calendar.

Configuration.py contains sensitive information. you can use `git update-index --assume-unchanged` to prevent it being committed to repository.


## Commands and Endpoints

- `/pto_apply` It will apply a PTO entry. Format is `/pto_apply name description start end`
	- Due to system limitation, description can be only a word. We usually uses *PTO* *WFH* most.
	- **start** is mandatory, if **end** is not specified, PTO will be made for 1 day.
	- Endpoint is `http://node.rayer.idv.tw:1200/pto/slack/apply`
- `/pto_calendar` Show link to google calendar which shows everyone's PTO.
	- Endpoint is `http://node.rayer.idv.tw:1200/pto/slack/cal`

## Server App

###D eployment

Currently our team slack setting is points to endpoints start from `http://node.rayer.idv.tw:1200/pto/slack/`. Will be configurable in future.


