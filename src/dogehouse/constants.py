READY = '_ready'

NEW_TOKENS = 'new-tokens'

CREATE_ROOM = 'room:create'
ROOM_CREATED = 'room:create:reply'
JOIN_ROOM = 'room:join'
ROOM_JOINED = 'room:join:reply'
GET_TOP_ROOMS = 'room:get_top'
ROOMS_FETCHED = 'room:get_top:reply'
DELETE_CHAT_MESSAGE = 'chat:delete'
BAN_CHAT_MEMBER = 'chat:ban'
UNBAN_CHAT_MEMBER = 'chat:unban'
BAN_ROOM_MEMBER = 'room:ban'
UNBAN_ROOM_MEMBER = 'room:unban'
FETCH_ROOM_BANNED_USERS = 'room:get_banned_users'

USER_JOINED = 'new_user_join_room'
USER_LEFT = 'user_left_room'
MESSAGE = 'chat:send'
CHAT_MESSAGE_DELETED = 'chat:delete'  # why is this the same as above???
CHAT_MEMBER_BANNED = 'chat_user_banned'
CHAT_MEMBER_UNBANNED = 'chat_user_unbanned'
#ROOM_MEMBER_BANNED = 'room_user_banned'
# ROOM_MEMBER_UNBANNED = 'room_user_unbanned' #These 2 have no reply, keep them until dogehouse implements one
FETCHED_ROOM_BANNED_USERS = 'room:get_banned_users:reply'

SEND_MESSAGE = 'send_room_chat_msg'
