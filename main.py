import os
import sys
import logging

from slack_sdk import WebClient

logging.basicConfig(level=logging.INFO)

channel_name='kind-machine'


def check_response(response):
    logging.info(f' {response.http_verb} {response.api_url} {response.status_code} {response.data}')
    if response.status_code != 200:
        logging.info(f' response status code not 200')
        return False
    elif not response.data['ok']:
        logging.info(f' response "ok" not True')
        return False
    return True


def main(args):
    token = os.environ['SLACK_BOT_TOKEN']
    print(f'token: {token}')

    client = WebClient(token=token)

    # test connectivity
    test_response = client.api_test()
    if not check_response(test_response):
        return

    # get users
    users_list_response = client.users_list()
    if not check_response(users_list_response):
        return

    # create user dict
    users= {}
    for user in users_list_response['members']:
        logging.info(f'{user}')
        users[user['id']]=user['name']

    # get channels
    conversations_list_response = client.conversations_list()
    if not check_response(conversations_list_response):
        return

    # filter out our channel
    matching_channels = [item for item in conversations_list_response['channels'] if item.get('name') == channel_name]
    if len(matching_channels) == 0:
        logging.info(f' conversations list request channels did not match "{channel_name}"')
        return
    matching_channel = matching_channels[0]

    # get messages
    conversations_history_response = client.conversations_history(channel=matching_channel['id'])
    if not check_response(conversations_history_response):
        return

    # filter out real text messages
    text_messages = [item for item in conversations_history_response['messages'] if item.get('user') and not item.get('subtype') and item.get('type') == 'message']
    for message in text_messages:
        user_id=message["user"]
        logging.info(f' {message["ts"]} {users[user_id]}: {message["text"]}')


if __name__ == '__main__':
    main(sys.argv[1:])
