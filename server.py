import os

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from fbmq import Page
from flask import Flask, request

from helper import *

chatterbot = ChatBot("Training Example")
chatterbot.set_trainer(ChatterBotCorpusTrainer)

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
page = Page(ACCESS_TOKEN)

raw_data, data = prepare_data()
zipped = map_icon_list()
page.show_starting_button("START_PAYLOAD")

page.show_persistent_menu([Template.ButtonPostBack('Information', 'PMENU_' + 'Information'),
                           Template.ButtonPostBack('Reach Us', 'PMENU_' + 'map')])


@page.callback(['START_PAYLOAD'])
def start_callback(payload, event):
    page.send(event.sender_id, "Welcome to Udaan 2018! Write down info to get information about various events")


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
                                    image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_INSTA'])
                                    ])
        ]))
        return 1
    if 'twitter' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Twitter',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_TWITTER'])
                                    ])
        ]))
        return 1
    if 'github' in message.lower():
        page.send(sender_id, Template.Generic([
            Template.GenericElement(title='Udaan18 Github',
                                    subtitle='The euphoric leap',
                                    image_url=CONFIG['UDAAN_URL'],
                                    buttons=[
                                        Template.ButtonWeb('Visit', CONFIG['UDAAN_GITHUB'])
                                    ])
        ]))
        return 1
    return 0


@page.handle_message
def message_handler(event):
    sender_id = event.sender_id
    message = event.message_text

    if message is None:
        return

    message_handled = 0
    categories_list = ['info', 'categories', 'category', 'details']
    reach_us_list = ['navigate', 'reach', 'map', 'bvm', 'birla', 'vishvakarma', 'mahavidyalaya', 'college']

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
        dept_list.append(raw_data['technical'][dept_idx]['alis'])
        if dept == 'ec/el':
            dept_list = ['electronics', 'communication']
        if dept == 'computer/it':
            dept_list = ['computer', 'information technology']

        for mdept in dept_list:
            if mdept.lower() in message.lower():
                callback_picked_dept(payload='PICK_' + dept, event=event, data=data, raw_data=raw_data, page=page)
                return

    # For displaying info related to categories
    for category in data[0]:
        if category.lower() in message.lower():
            if category.lower() == 'technical' and 'non' in message.lower():
                callback_picked_category(payload='CATEGORY__non-technical', event=event, data=data, raw_data=raw_data,
                                         page=page)
            else:
                callback_picked_category(payload='CATEGORY__' + category, event=event, data=data, raw_data=raw_data,
                                         page=page)
            return
    non_tech_keywords = ['non-tech', 'nontech']
    for non_tech_keyword in non_tech_keywords:
        if non_tech_keyword in message.lower():
            callback_picked_category(payload='CATEGORY__non-technical', event=event, data=data, raw_data=raw_data,
                                     page=page)
            return
    if 'tech' in message.lower():
        callback_picked_category(payload='CATEGORY__technical', event=event, data=data, raw_data=raw_data,
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
    if 'fine' in message.lower():
        page.send(sender_id, 'Good')
    bot_input = chatterbot.get_response(message)
    if 'do you feel' in str(bot_input).lower():
        page.send(sender_id, 'Good')
        return
    else:
        print(bot_input)
        page.send(recipient_id=sender_id, message=str(bot_input))

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
    app.run()
