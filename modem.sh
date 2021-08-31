#!/bin/sh
MODEM_IP="192.168.8.1"
curl -s -X GET "http://$MODEM_IP/api/webserver/SesTokInfo" > /tmp/ses_tok.xml
COOKIE=`grep "SessionID=" /tmp/ses_tok.xml | cut -b 10-147`
TOKEN=`grep "TokInfo" /tmp/ses_tok.xml | cut -b 10-41`
if [ "$1" = "status" ]; then
curl -s -X GET -H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" -H "Content-type: text/xml" http://$MODEM_IP/api/dialup/mobile-dataswitch
elif [ "$1" = "stop" ]; then
curl -s -X POST -H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" -H "Content-type: text/xml" -d "<response><dataswitch>0</dataswitch></response>" http://$MODEM_IP/api/dialup/mobile-dataswitch >/dev/null 2>&1
elif [ "$1" = "start" ]; then
curl -s -X POST -H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" -H "Content-type: text/xml" -d "<response><dataswitch>1</dataswitch></response>" http://$MODEM_IP/api/dialup/mobile-dataswitch >/dev/null 2>&1
elif [ "$1" = "sms" ]; then
curl -v http://$MODEM_IP/api/sms/send-sms -H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  --data "<?xml version='1.0' encoding='UTF-8'?><request><Index>-1</Index><Phones><Phone>$2</Phone></Phones><Sca></Sca><Content>$3</Content><Length>160</Length><Reserved>1</Reserved><Date>-1</Date></request>"
fi