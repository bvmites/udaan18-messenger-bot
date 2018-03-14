from fbmq import QuickReply, Template

from CONFIG import CONFIG


def display_categories(sender_id, data, page):
    quick_replies = []
    for category in data[0]:
        quick_replies.append(QuickReply(title=category, payload='CATEGORY__' + category))
    page.send(sender_id,
              "Please Select a Category",
              quick_replies=quick_replies,
              metadata="DEVELOPER_DEFINED_METADATA")


def callback_clicked_other(payload, event, data, raw_data, page):
    sender_id = event.sender_id
    message = payload.split('_')[1]
    print(message)
    category_idx = -1
    event_idx = -1

    for event_list in data[1]:
        for event_name in event_list:
            if event_name == message:
                category_idx = data[1].index(event_list)
                event_idx = event_list.index(event_name)

    if category_idx == -1:
        return

    category_name = data[0][category_idx]

    event_raw_data = raw_data[category_name][event_idx]
    round_str = ''
    for n, round in enumerate(event_raw_data['rounds'], 1):
        round_str += 'Round ' + str(n) + ':'
        round_str += '\n' + str(round) + '\n\n'
    generic_list = [Template.GenericElement(title=event_raw_data['name'], subtitle=event_raw_data['tagline'],
                                            image_url=CONFIG['UDAAN_URL']),
                    Template.GenericElement(title='Entry Fee: ', subtitle=event_raw_data['fees'])]
    managers = [Template.ButtonPhoneNumber("Call Manager", "+91" + str(event_raw_data['managers'][i]['phone']))
                for i in range(0, len(event_raw_data['managers'])) if i < 1]
    send_str = round_str

    page.send(sender_id, Template.List(
        elements=generic_list,
        top_element_style='large',
        buttons=managers

    ))
    page.send(sender_id, send_str)


def callback_clicked_tech(payload, event, data, raw_data, page):
    sender_id = event.sender_id
    message = payload.split('_')[1]
    print(message)
    category_idx = -1
    event_idx = -1

    for event_list in data[2]:
        for event_name in event_list:
            if event_name == message:
                category_idx = data[2].index(event_list)
                event_idx = event_list.index(event_name)

    if category_idx == -1:
        return

    event_raw_data = raw_data['technical'][category_idx]['events'][event_idx]
    print(event_raw_data)
    round_str = ''
    for n, my_round in enumerate(event_raw_data['rounds'], 1):
        round_str += 'Round ' + str(n) + ':'
        round_str += '\n' + str(my_round) + '\n\n'

    generic_list = [Template.GenericElement(title=event_raw_data['name'], subtitle=event_raw_data['tagline'],
                                            image_url=CONFIG['UDAAN_URL']),
                    Template.GenericElement(title='Entry Fee: ', subtitle=event_raw_data['fees'])]

    managers = [Template.ButtonPhoneNumber("Call Manager", "+91" + str(event_raw_data['managers'][i]['phone']))
                for i in range(0, len(event_raw_data['managers'])) if i < 1]
    send_str = round_str

    page.send(sender_id, Template.List(
        elements=generic_list,
        top_element_style='large',
        buttons=managers

    ))
    page.send(sender_id, send_str)


def callback_picked_dept(payload, event, data, raw_data, page):
    sender_id = event.sender_id
    message = payload.split('_')[1]
    print(message)
    tech_idx = data[0].index('technical')
    if message.lower() in [dept for dept in data[1][tech_idx]]:
        dept_idx = data[1][tech_idx].index(message)
        generic_template = []
        for event in data[2][dept_idx]:
            generic_template.append(Template.GenericElement(event,
                                                            subtitle=data[1][tech_idx][dept_idx],
                                                            image_url=CONFIG['UDAAN_URL'],
                                                            buttons=[
                                                                Template.ButtonPhoneNumber("Contact", '+91' +
                                                                                           raw_data['technical'][
                                                                                               dept_idx]['events'][
                                                                                               data[2][dept_idx].index(
                                                                                                   event)]['managers'][
                                                                                               0]['phone']),
                                                                Template.ButtonPostBack('Details', "TECH_" + event)
                                                            ]))
        page.send(sender_id, Template.Generic(generic_template))


def callback_picked_category(payload, event, data, raw_data, page):
    sender_id = event.sender_id
    message = payload.split('__')[1]
    idx = data[0].index(message)
    quick_replies = []

    if message == 'technical':
        for category in data[1][idx]:
            quick_replies.append(QuickReply(title=category, payload='PICK_' + category))
        page.send(sender_id,
                  "Please Select a department",
                  quick_replies=quick_replies,
                  metadata="DEVELOPER_DEFINED_METADATA")
    else:
        generic_template = []
        i = 1
        for event in data[1][idx]:
            generic_template.append(Template.GenericElement(event,
                                                            subtitle=message,
                                                            image_url=CONFIG['UDAAN_URL'],
                                                            buttons=[
                                                                Template.ButtonPhoneNumber("Contact", '+91' +
                                                                                           raw_data[message][
                                                                                               data[1][idx].index(
                                                                                                   event)]['managers'][
                                                                                               0]['phone']),
                                                                Template.ButtonPostBack('Details', "OTHER_" + event)
                                                            ]))
            i += 1
        if i > 20:
            page.send(sender_id, Template.Generic([generic_template[z] for z in range(0, 10)]))
            page.send(sender_id, Template.Generic([generic_template[z] for z in range(10, 20)]))
            page.send(sender_id, Template.Generic([generic_template[z] for z in range(20, len(generic_template))]))
        elif i > 10:
            page.send(sender_id, Template.Generic([generic_template[z] for z in range(0, 10)]))
            page.send(sender_id, Template.Generic([generic_template[z] for z in range(10, len(generic_template))]))
        elif i <= 10:
            page.send(sender_id, Template.Generic(generic_template))
