import os

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from fbmq import Page
from flask import Flask, request

from CONFIG import CONFIG
from helper import *

chatterbot = ChatBot("Training Example")
chatterbot.set_trainer(ChatterBotCorpusTrainer)

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
page = Page(ACCESS_TOKEN)

raw_data, data, developers_data, team_udaan_data = prepare_data()
zipped = map_icon_list()
page.show_starting_button("START_PAYLOAD")

page.show_persistent_menu([Template.ButtonPostBack('Information', 'PMENU_' + 'Information'),
                           Template.ButtonPostBack('Reach Us', 'PMENU_' + 'map')])


@page.callback(['START_PAYLOAD'])
def start_callback(payload, event):
    page.send(event.sender_id, "Welcome to Udaan 2018! Write down info to get information about various events.")

    page.send(event.sender_id, "Find details of individuals events: \"Give me details of Hardwizard \"")
    page.send(event.sender_id, "Find list of events: \"tech events\"")


@app.route('/', methods=['GET', 'POST'])
def validate():
    if request.method == 'GET':
        if request.args.get('hub.mode', '') == 'subscribe' and \
                request.args.get('hub.verify_token', '') == VERIFY_TOKEN:

            print("Validating webhook")
            return request.args.get('hub.challenge', '')

        else:
            return 'Failed validation. Make sure the validation tokens match.'
    elif request.method == 'POST':
        page.handle_webhook(request.get_data(as_text=True))
        return "ok"


def social_media_handle(message, sender_id):
    """
    Handles Social Media Keywords
    :param message: message from user
    :param sender_id: users id
    :return: 0 if keyword not found, else 1
    """
    if 'website' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Website',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Visit Website', CONFIG['UDAAN_WEBSITE'])
                                    ])
        ]))
        return 1
    if 'insta' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Instagram',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['SOCIAL_BASE_LINK'] + 'instagram.png',
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_INSTA'])
                                    ])
        ]))
        return 1
    if 'twitter' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Twitter',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['SOCIAL_BASE_LINK'] + 'twitter.png',
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_TWITTER'])
                                    ])
        ]))
        return 1
    if 'github' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Github',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['SOCIAL_BASE_LINK'] + 'github.png',
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_GITHUB'])
                                    ])
        ]))
        return 1
    return 0


def team_udaan_handler(event):
    message = event.message_text
    sender_id = event.sender_id
    ge_list = []
    team_categories = [team_udaan['category'] for team_udaan in team_udaan_data]
    team_categories[team_categories.index('Technical')] = 'Tech Head'
    team_udaan_key_list = ['teamudaan', 'team udaan', 'team-udaan', 'udaan team', 'udaanteam']
    for z, category in enumerate(team_categories, 0):
        if category.lower() in message.lower():
            ge_list = [Template.GenericElement(title=team_udaan_data[z]['members'][i]['name'],
                                               subtitle=team_udaan_data[z]['category'] + ' - '
                                                        + team_udaan_data[z]['members'][i]['title'],
                                               image_url=CONFIG['UDAAN_URL'],
                                               buttons=[
                                                   Template.ButtonPhoneNumber('Contact',
                                                                              team_udaan_data[z]['members'][i][
                                                                                  'mobile'])
                                               ]) for i in range(0, len(team_udaan_data[z]['members']))]
            page.send(sender_id, Template.Generic(ge_list))
            return 1
    for keyword in team_udaan_key_list:
        if keyword.lower() in message.lower():
            for z, category in enumerate(team_udaan_data, 0):
                for member in category['members']:
                    ge_list.append(Template.GenericElement(title=member['name'],
                                                           subtitle=category['category'] + ' - ' + member['title'],
                                                           image_url=CONFIG['UDAAN_URL'],
                                                           buttons=[
                                                               Template.ButtonPhoneNumber('Contact',
                                                                                          member['mobile'])]))

            page.send(sender_id, Template.Generic(ge_list[0:10]))
            page.send(sender_id, Template.Generic(ge_list[10:20]))
            page.send(sender_id, Template.Generic(ge_list[20:]))
            return 1

    for z, category in enumerate(team_udaan_data, 0):
        for member in category['members']:
            if member['name'].lower() in message.lower():
                page.send(sender_id, Template.Generic([Template.GenericElement(title=member['name'],
                                                                               subtitle=category['category'] + ' - ' +
                                                                                        member['title'],
                                                                               image_url=CONFIG['UDAAN_URL'],
                                                                               buttons=[
                                                                                   Template.ButtonPhoneNumber('Contact',
                                                                                                              member[
                                                                                                                  'mobile'])])]))
                return 1
    return 0


def developer_details_handler(event):
    message = event.message_text
    sender_id = event.sender_id
    developer_list = ['developer', 'creator', 'created', 'maker']

    ge_list = []
    for developer in developers_data:
        ge_list.append(Template.GenericElement(title=developer['name'],
                                               subtitle=developer['category'].upper() + ' - ' + developer['title'],
                                               image_url=CONFIG['UDAAN_URL'],
                                               buttons=[
                                                   Template.ButtonWeb(title='Github', url=developer['github']),
                                                   Template.ButtonPhoneNumber(title='Contact',
                                                                              payload=developer['mobile'])
                                               ]))
    for dev in developer_list:
        if dev.lower() in message.lower():
            page.send(sender_id, Template.Generic(ge_list[0:9]))
            page.send(sender_id, Template.Generic(ge_list[9:]))
            return 1

    # Individual Name Cards
    for developer in developers_data:
        if developer['name'].lower() in message.lower():
            page.send(sender_id, Template.Generic([Template.GenericElement(title=developer['name'],
                                                                           subtitle=developer[
                                                                                        'category'].upper() + ' - ' +
                                                                                    developer['title'],
                                                                           image_url=CONFIG['UDAAN_URL'],
                                                                           buttons=[
                                                                               Template.ButtonWeb(title='Github',
                                                                                                  url=developer[
                                                                                                      'github']),
                                                                               Template.ButtonPhoneNumber(
                                                                                   title='Contact',
                                                                                   payload=developer['mobile'])
                                                                           ])]))
            return 1
    return 0


@page.handle_message
def message_handler(event):
    try:
        sender_id = event.sender_id
        message = event.message_text

        if message is None:
            return

        message_handled = 0
        categories_list = ['info', 'categories', 'category', 'details', 'event', 'events']
        reach_us_list = ['navigate', 'reach', 'map', 'bvm', 'birla', 'vishvakarma', 'mahavidyalaya', 'college', 'where']

        # Handle Developer queries
        if developer_details_handler(event) == 1:
            return

        # Handle Team Udaan queries
        if team_udaan_handler(event) == 1:
            return
        # Handle Social Media Queries
        if social_media_handle(message, sender_id) == 1:
            return
        if ('when' in message.lower() and 'udaan' in message.lower()) or message.lower() == 'when':
            page.send(sender_id, '2nd, 3rd and 4th April, 2018 :)')
            page.send(sender_id, 'We look forward to seeing you there')
            return
        if ('where' in message.lower() and 'udaan' in message.lower()) or message.lower() == 'where':
            click_persistent_menu(payload='PMENU_' + 'map', event=event)
            return
        if message.lower() in 'hey hello hi there hey there':
            page.send(sender_id, 'Hey there! How you doing?')
            start_callback('START_PAYLOAD', event=event)
            return
        # For handling inputs related to tech events
        for tech_dept in data[2]:
            for tech_event in tech_dept:
                if tech_event.lower() in message.lower():
                    callback_clicked_tech(payload='TECH_' + tech_event, event=event, data=data, raw_data=raw_data,
                                          page=page)
                    message_handled = 1

        # For handling inputs related to other events
        for z, category in enumerate(data[1], 0):
            if z == data[0].index('technical'):  # Ignore technical events
                continue
            for other_event in category:
                if other_event.lower() in message.lower():
                    callback_clicked_other(payload='OTHER_' + other_event, event=event, data=data, raw_data=raw_data,
                                           page=page)
                    message_handled = 1

        if message_handled == 1:
            return

        # For displaying department events
        for dept_idx, dept in enumerate(data[1][data[0].index('technical')], 0):
            dept_list = dept.split('/')
            dept_list.append(raw_data['technical'][dept_idx]['alis'].lower())
            if dept == 'ec/el':
                dept_list = ['electronics', 'communication', 'Sonic-A-Tronics', 'sonicatronics', 'sonic a tronics',
                             'sonicatronics', 'ec/el']
            if dept == 'computer/it':
                dept_list = ['computer', 'information technology', 'coders squad', 'coders-squad', "coder's squad",
                             'coderssquad']
            if dept == 'electrical':
                dept_list.append("Dynamo-Bombers")
                dept_list.append("dynamo bombers")
                dept_list.append('dynamobombers')
            if dept == 'civil':
                dept_list.append('inframaniacs')
            for mdept in dept_list:
                if mdept.lower() in message.lower():
                    callback_picked_dept(payload='PICK_' + dept, event=event, data=data, raw_data=raw_data, page=page)
                    return

        # For displaying info related to categories
        for category in data[0]:
            if category.lower() in message.lower():
                if category.lower() == 'technical' and 'non' in message.lower():
                    callback_picked_category(payload='CATEGORY__non-technical', event=event, data=data,
                                             raw_data=raw_data,
                                             page=page)
                else:
                    callback_picked_category(payload='CATEGORY__' + category, event=event, data=data, raw_data=raw_data,
                                             page=page)
                return
        non_tech_keywords = ['non-tech', 'nontech', 'pandora box', 'pandorabox', 'non tech']
        for non_tech_keyword in non_tech_keywords:
            if non_tech_keyword in message.lower():
                callback_picked_category(payload='CATEGORY__non-technical', event=event, data=data, raw_data=raw_data,
                                         page=page)
                return
        if 'tech' in message.lower() or 'department' in message.lower():
            callback_picked_category(payload='CATEGORY__technical', event=event, data=data, raw_data=raw_data,
                                     page=page)
            return
        cultural_keywords = ['mad house', 'madhouse']
        for cultural_keyword in cultural_keywords:
            if cultural_keyword in message.lower():
                callback_picked_category(payload='CATEGORY__cultural', event=event, data=data, raw_data=raw_data,
                                         page=page)
                return
        girls_keywords = ['fab famina', 'fabfamina']
        for girls_keyword in girls_keywords:
            if girls_keyword in message.lower():
                callback_picked_category(payload='CATEGORY__girls', event=event, data=data, raw_data=raw_data,
                                         page=page)
                return
        adventure_keywords = ['Diagon Alley', 'diagonalley']
        for adventure_keyword in adventure_keywords:
            if adventure_keyword in message.lower():
                callback_picked_category(payload='CATEGORY__adventure', event=event, data=data, raw_data=raw_data,
                                         page=page)
                return

        # Reach us
        for keyword in reach_us_list:
            if keyword.lower() in message.lower():
                click_persistent_menu(payload='PMENU_' + 'map', event=event)
                return

        # Level 0 Menu
        for keyword in categories_list:
            if keyword.lower() in message.lower():
                click_persistent_menu(payload='PMENU_' + 'Information', event=event)
                return
        # udaan
        if 'udaan' in message.lower():
            start_callback('START_PAYLOAD', event=event)
            return
        if 'fine' in message.lower():
            page.send(sender_id, 'Good')
            return
        bot_input = chatterbot.get_response(message)
        if 'do you feel' in str(bot_input).lower():
            page.send(sender_id, 'Good')
        else:
            print(bot_input)
            page.send(sender_id, str(bot_input))
    except Exception as e:
        print(e)
        page.send(event.sender_id, 'Hello')


@page.callback(['CATEGORY__(.+)'])
def callback_picked_genre(payload, event):
    # callback_picked_category(payload, event)
    pass


@page.callback(['OTHER_(.+)'])
def callback_clicked_button(payload, event):
    callback_clicked_other(payload=payload, event=event, data=data, raw_data=raw_data, page=page)


@page.callback(['PICK_(.+)'])
def callback_picked_genre(payload, event):
    # callback_picked_dept(payload, event)
    pass


@page.callback(['TECH_(.+)'])
def callback_clicked_button(payload, event):
    callback_clicked_tech(payload=payload, event=event, data=data, raw_data=raw_data, page=page)


@page.callback(['PMENU_(.+)'])
def click_persistent_menu(payload, event):
    message = payload.split('_')[1]
    if message == 'Information':
        display_categories(sender_id=event.sender_id, page=page, data=data)
    if message == 'map':
        page.send(event.sender_id, Template.Generic([
            Template.GenericElement(title='Birla Vishvarkarma Mahavidyalaya', subtitle='Udaan 18 - 2nd, 3rd, 4th April',
                                    image_url=CONFIG['BVM_LOGO'],
                                    buttons=[
                                        Template.ButtonWeb("Navigate", CONFIG['BVM_ADDRESS'])]
                                    ),
            Template.GenericElement(title='Contact Us', subtitle='', image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Website', CONFIG['UDAAN_WEBSITE']),
                                        Template.ButtonWeb('Instagram', CONFIG['UDAAN_INSTA']),
                                    ]),
            Template.GenericElement(title='Contact Us', subtitle='', image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Twitter', CONFIG['UDAAN_TWITTER']),
                                        Template.ButtonWeb('Github', CONFIG['UDAAN_GITHUB']),
                                    ])
        ]))


if __name__ == '__main__':
    app.run(threaded=True)
