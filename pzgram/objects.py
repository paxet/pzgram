import os

from .parsing import message_types, parse_forward_reply
from .useful import message_all_attributes as message_all
from .useful import chat_all_attributes as chat_all
from .useful import user_all_attirbutes as user_all
from .useful import chat_member_all_attributes as chat_mem_all
from .useful import *

from .media_objects import *


class Message:
    def __init__(self, bot, message_dict):
        self.bot = bot
        # Find the type of this message
        for t in message_types:
            if t in message_dict:
                self.type = t
                # Call the connected method for parsing that type of message
                message_dict = message_types[t](message_dict, bot)
                break
        # Parse other things
        message_dict = parse_forward_reply(message_dict, bot)
        # Add all possbile attributes to message_dict and set to None
        for i in message_all:
            if i not in message_dict:
                message_dict[i] = None
        # Delete attribute from and replace with sender
        # FIXME: Check if this work with Channels
        message_dict["sender"] = User(bot, message_dict["from"])
        message_dict.pop("from")
        message_dict["chat"] = Chat(bot, message_dict["chat"]["id"], message_dict["chat"])
        # Memorize all attributes
        for i in message_dict:
            setattr(self, i, message_dict[i])

    def __str__(self):
        return "MessageObject{Type:" + self.type + " From:" + str(self.chat.id) + "}"

    def __repr__(self):
        return "MessageObject" + str(self.message_id)

    def forward(self, chat_id, notification=True):
        param = {
            "chat_id": chat_id,
            "from_chat_id": self.chat.id,
            "message_id": self.message_id,
            "disable_notification": not notification
        }
        return Message(self.bot, api_request(self.bot, "forwardMessage", param=param))

    def delete(self):
        param = {
            "chat_id": self.chat.id,
            "message_id": self.message_id
        }
        return api_request(self.bot, "deleteMessage", param=param)

    def reply(self, text, **kwargs):
        return self.chat.send(text, reply_to=self.message_id, **kwargs)

    def reply_photo(self, photopath, **kwargs):
        return self.chat.send_photo(photopath, reply_id=self.message_id, **kwargs)

    def reply_voice(self, voicepath, **kwargs):
        return self.chat.send_voice(voicepath, reply_id=self.message_id, **kwargs)

    def reply_audio(self, audiopath, **kwargs):
        return self.chat.send_audio(audiopath, reply_id=self.message_id, **kwargs)

    def reply_document(self, documentpath, **kwargs):
        return self.chat.send_document(documentpath, reply_id=self.message_id, **kwargs)

    def reply_video(self, videopath, **kwargs):
        return self.chat.send_video(videopath, reply_id=self.message_id, **kwargs)

    def reply_videonote(self, videonotepath, **kwargs):
        return self.chat.send_video(videonotepath, reply_id=self.message_id, **kwargs)

    def reply_contact(self, phone_number, first_name, **kwargs):
        return self.chat.send_contact(phone_number, first_name, reply_id=self.message_id, **kwargs)

    def reply_location(self, latitude, longitude, **kwargs):
        return self.chat.send_location(latitude, longitude, reply_id=self.message_id, **kwargs)

    def reply_venue(self, latitude, longitude, title, address, **kwargs):
        return self.chat.send_venue(latitude, longitude, title, address, reply_id=self.message_id, **kwargs)


class Chat:
    def __init__(self, bot, id, chat_dict=dict()):
        self.bot = bot
        # For all attributes, check if is in the dict, otherwise set to None
        for i in chat_all:
            if i in chat_dict:
                setattr(self, i, chat_dict[i])
            else:
                setattr(self, i, None)
        self.id = id
        # Parse pinned_message and photo if they are not None (only returned in getChat)
        if self.pinned_message is not None:
            self.pinned_message = Message(bot, self.pinned_message)
        if self.photo is not None:
            # TODO
            pass

    def __str__(self):
        if self.type == "private":
            m = "Name:" + self.first_name
        else:
            m = "Title:" + self.title
        return "ChatObject{Id:" + str(self.id) + " " + m + "}"

    def __repr__(self):
        return "ChatObject" + str(self.id)

    def get_info(self):
        p = {"chat_id": self.id}
        chat = api_request(self.bot, "getChat", p)
        return Chat(self.bot, chat["id"], chat)

    def send(self, text, parse_mode="markdown", preview=True, notification=True, reply_to=None, reply_markup=None):
        param = {
            "chat_id": self.id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": not preview,
            "disable_notification": notification,
            "reply_to_message_id": reply_to,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendMessage", param))

    def forward_message(self, message_id, chat_id, notification=True):
        param = {
            "chat_id": chat_id,
            "from_chat_id": self.id,
            "message_id": message_id,
            "disable_notification": not notification
        }
        return Message(self.bot, api_request(self.bot, "forwardMessage", param=param))

    def delete_message(self, message_id):
        param = {
            "chat_id": self.id,
            "message_id": message_id
        }
        return api_request(self.bot, "deleteMessage", param=param)

    def send_action(self, action):
        param = {"chat_id": self.id, "action": action}
        return api_request(self.bot, "sendChatAction", param)

    def send_photo(self, photopath, caption=None, parse_mode=None, notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(photopath):
            raise FileNotFoundError("File " + photopath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(photopath)
        file = {
            "photo": (name, open(photopath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendPhoto", param, file))

    def send_voice(self, voicepath, duration=None, caption=None, parse_mode=None,
                   notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(voicepath):
            raise FileNotFoundError("File " + voicepath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(voicepath)
        file = {
            "voice": (name, open(voicepath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "duration": duration,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendVoice", param, file))

    def send_audio(self, audiopath, duration=None, performer=None, title=None, caption=None, parse_mode=None,
                   notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(audiopath):
            raise FileNotFoundError("File " + audiopath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(audiopath)
        file = {
            "audio": (name, open(audiopath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "duration": duration,
            "performer": performer,
            "title": title,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendAudio", param, file))

    def send_document(self, documentpath, caption=None, parse_mode=None,
                      notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(documentpath):
            raise FileNotFoundError("File " + documentpath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(documentpath)
        file = {
            "document": (name, open(documentpath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendDocument", param, file))

    def send_video(self, videopath, duration=None, width=None, height=None, caption=None, parse_mode=None,
                   support_streaming=None, notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(videopath):
            raise FileNotFoundError("File " + videopath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(videopath)
        file = {
            "video": (name, open(videopath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "duration": duration,
            "width": width,
            "height": height,
            "caption": caption,
            "parse_mode": parse_mode,
            "support_straming": support_streaming,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendVideo", param, file))

    def send_videonote(self, videonotepath, duration=None, length=None,
                       notification=True, reply_id=None, reply_markup=None):
        # Check if file exists
        if not os.path.isfile(videonotepath):
            raise FileNotFoundError("File " + videonotepath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(videonotepath)
        file = {
            "video_note": (name, open(videonotepath, "rb"))
        }
        param = {
            "chat_id": self.id,
            "duration": duration,
            "length": length,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendVideoNote", param, file))

    def send_contact(self, phone_number, first_name, last_name=None, user_id=None,
                     notification=True, reply_id=None, reply_markup=None):
        param = {
            "chat_id": self.id,
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "user_id": user_id,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendContact", param))

    def send_location(self, latitude, longitude, live_period=None, notification=True, reply_id=None, reply_markup=None):
        param = {
            "chat_id": self.id,
            "latitude": latitude,
            "longitude": longitude,
            "live_period": live_period,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendLocation", param))

    def send_venue(self, latitude, longitude, title, address, foursquare_id=None,
                   notification=True, reply_id=None, reply_markup=None):
        param = {
            "chat_id": self.id,
            "latitude": latitude,
            "longitude": longitude,
            "title": title,
            "address": address,
            "foursquare_id": foursquare_id,
            "disable_notification": not notification,
            "reply_to_message_id": reply_id,
            "reply_markup": reply_markup
        }
        return Message(self.bot, api_request(self.bot, "sendVenue", param))

    def kick_user(self, user_id, until_date=None):
        if self.type == "private":
            raise WrongChatTypeError("You can't kick someone from a private Chat")
        p = {
            "chat_id": self.id,
            "user_id": user_id,
            "until_date": until_date
        }
        return api_request(self.bot, "kickChatMember", p)

    def unban_user(self, user_id):
        if self.type == "private":
            raise WrongChatTypeError("You can't unban someone from a private Chat")
        p = {"chat_id": self.id, "user_id": user_id}
        return api_request(self.bot, "unbanChatMember")

    def restrict_user(self, user_id, until_date=None,
                      send_message=None, send_media=None, send_other=None, web_page_preview=None):
        if self.type != "supergroup":
            raise WrongChatTypeError("RestrictUser can only be used in supergroups")
        p = {
            "chat_id": self.id,
            "user_id": user_id,
            "until_date": until_date,
            "can_send_messages": send_message,
            "can_send_media_messages": send_media,
            "can_send_other_messages": send_other,
            "can_add_web_page_previews": web_page_preview
        }
        return api_request(self.bot, "restrictChatMember", p)

    def promote_user(self, user_id, change_info=None, post_message=None, edit_message=None, delete_message=None,
                     invite_user=None, restrict_user=None, pin_message=None, promote_user=None):
        if self.type != "supergroup" and self.type != "channel":
            raise WrongChatTypeError("PromoteUser can only be used in supergroups or channels")
        p = {
            "chat_id": self.id,
            "user_id": user_id,
            "can_change_info": change_info,
            "can_post_messages": post_message,
            "can_edit_messages": edit_message,
            "can_delete_message": delete_message,
            "can_invite_users": invite_user,
            "can_restrict_users": restrict_user,
            "can_pin_messages": pin_message,
            "can_promote_users": promote_user
        }
        return api_request(self.bot, "promoteChatMember", p)

    def new_invite_link(self):
        return api_request(self.bot, "exportChatInviteLink", {"chat_id": self.id})

    def set_photo(self, photopath):
        # Check if file exists
        if not os.path.isfile(photopath):
            raise FileNotFoundError("File " + photopath + " not exists or is a folder")
        # Find the name of that file from his path
        name = file_name(photopath)
        file = {
            "photo": (name, open(photopath, "rb"))
        }
        return api_request(self.bot, "setChatPhoto", {"chat_id": self.id}, file)

    def delete_photo(self):
        if self.type == "private":
            raise WrongChatTypeError("DeleteChatPhoto can only be used in groups or channels")
        return api_request(self.bot, "deleteChatPhoto", {"chat_id": self.id})

    def set_title(self, title):
        if self.type == "private":
            raise WrongChatTypeError("SetChatTitle can only be used in groups or channels")
        return api_request(self.bot, "setChatTitle", {"chat_id": self.id, "title": title})

    def set_description(self, description):
        if self.type == "private" or self.type == "group":
            raise WrongChatTypeError("SetChatDescription can only be used in supergroups or channels")
        return api_request(self.bot, "setChatTitle", {"chat_id": self.id, "description": description})

    def pin_message(self, message_id, notification=True):
        if self.type == "private" or self.type == "group":
            raise WrongChatTypeError("PinMessage can only be used in supergroups or channels")
        p = {
            "chat_id": self.id,
            "message_id": message_id,
            "disable_notification": not notification
        }
        return api_request(self.bot, "pinChatMessage", p)

    def unpin_message(self):
        if self.type == "private" or self.type == "group":
            raise WrongChatTypeError("unPinMessage can only be used in supergroups or channels")
        api_request(self.bot, "unpinChatMessage", {"chat_id": self.id})

    def leave(self):
        if self.type == "private":
            raise WrongChatTypeError("LeaveChat can only be used in groups or channels")
        api_request(self.bot, "leaveChat", {"chat_id": self.id})

    def get_admnistrator(self):
        if self.type == "private":
            raise WrongChatTypeError("LeaveChat can only be used in groups or channels")
        # Return a list of ChatMember objects, each rappresenting a single admin
        users = api_request(self.bot, "getChatAdministrator", {"chat_id": self.id})
        admins = []
        for u in users:
            admins.append(ChatMember(self.bot, u))
        return admins

    def get_member_count(self):
        if self.type == "private":
            raise WrongChatTypeError("LeaveChat can only be used in groups or channels")
        return api_request(self.bot, "getChatMembersCount", {"chat_id": self.id})

    def get_member(self, user_id):
        if self.type == "private":
            raise WrongChatTypeError("LeaveChat can only be used in groups or channels")
        return ChatMember(self.bot, api_request(self.bot, "getChatMember", {"chat_id": self.id, "user_id": user_id}))


class User:
    def __init__(self, bot, user_dict):
        self.bot = bot
        # For all attributes, check if is in the dict, otherwise set to None
        for i in user_all:
            if i in user_dict:
                setattr(self, i, user_dict[i])
            else:
                setattr(self, i, None)

    def __str__(self):
        if self.is_bot:
            return "UserObject{Id:" + str(self.id) + " Name:" + self.first_name + " IsBot: True}"
        else:
            return "UserObject{Id:" + str(self.id) + " Name:" + self.first_name + "}"

    def __repr__(self):
        return "UserObject" + str(self.id)

    def get_profile_photos(self, offset=None, limit=None):
        # Offset from the first, default send the last 100 profile photos
        p = {
            "user_id": self.id,
            "offset": offset,
            "limit": limit
        }
        photos_dict = api_request(self.bot, "getUserProfilePhotos", p)
        # List of List of PhotoSize (Each photo has more sizes)
        photos = []
        for i in photos_dict["photos"]:
            # For each Photo
            photo = []
            for j in i:
                # For each size
                photo.append(Photo(self.bot, j))
            photos.append(photo)
        return photos

    def send(self, text, **kwargs):
        return Chat(self.bot, self.id).send(text, **kwargs)

    def send_photo(self, photopath, **kwargs):
        return Chat(self.bot, self.id).send_photo(photopath, **kwargs)

    def send_voice(self, voicepath, **kwargs):
        return Chat(self.bot, self.id).send_voice(voicepath, **kwargs)

    def send_audio(self, audiopath, **kwargs):
        return Chat(self.bot, self.id).send_audio(audiopath, **kwargs)

    def send_document(self, documentpath, **kwargs):
        return Chat(self.bot, self.id).send_document(documentpath, **kwargs)

    def send_video(self, videopath, **kwargs):
        return Chat(self.bot, self.id).send_video(videopath, **kwargs)

    def send_videonote(self, videonotepath, **kwargs):
        return Chat(self.bot, self.id).send_video(videonotepath, **kwargs)

    def send_contact(self, phone_number, first_name, **kwargs):
        return Chat(self.bot, self.id).send_contact(phone_number, first_name, **kwargs)

    def send_location(self, latitude, longitude, **kwargs):
        return Chat(self.bot, self.id).send_location(latitude, longitude, **kwargs)

    def send_venue(self, latitude, longitude, title, address, **kwargs):
        return Chat(self.bot, self.id).send_location(latitude, longitude, title, address, **kwargs)


class ChatMember(User):
    def __init__(self, bot, user_dict):
        # Call the User init, and after, set the attributes of a ChatMember
        User.__init__(self, bot, user_dict["user"])
        user_dict.pop("user", None)
        for i in chat_mem_all:
            if i in user_dict:
                setattr(self, i, user_dict[i])
            else:
                setattr(self, i, None)
