import asyncio
import vkreal
from config import token, posts, db_session
from check_func import check_admin, check_super_admin, get_user_id
from data.user import User
from data.requests import Request


async def hello(vk, event):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == event['from_id']).first()
    print(user)
    if not user:
        user = User(user_id=event['from_id'])
        db_sess.add(user)
        db_sess.commit()
    db_sess.close()
    await vk.messages_send(message="Привет! Используй !связаться <текст>, чтобы связаться с администрацией", peer_id=event['peer_id'], random_id=0)


async def get_request(vk, event):
    data = event['text'].split()
    if len(data) == 1:
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Используйте !связаться <текст>")
    else:
        db_sess = db_session.create_session()
        request = Request(request=' '.join(data[1:]), user_id=event['from_id'])
        db_sess.add(request)
        db_sess.commit()
        request = db_sess.query(Request).all()[-1]
        await vk.messages_send(peer_id=2000000001, random_id=0, message=f"Новое обращение!\n"
                                                                        f"ID: {request.id}\n"
                                                                        f"Содержимое запроса: {' '.join(data[1:])}")
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message='Ваша заявка успешно принята!')


async def answer_on_request(vk, event):
    data = event['text'].split()
    if len(data) <= 2:
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Используйте !ответ <id запроса> <ответ>")
    else:
        req_id = int(data[1])
        db_sess = db_session.create_session()
        request = db_sess.query(Request).filter(Request.id == req_id).first()
        answer = ' '.join(data[2:])
        await vk.messages_send(peer_id=request.user_id, random_id=0, message=f"Администрация ответила на ваш запрос! "
                                                                             f"Вот ответ:\n{answer}")
        db_sess.delete(request)
        db_sess.commit()
        user = db_sess.query(User).filter(User.user_id == event['from_id']).first()
        user.loyal += 1
        db_sess.commit()
        db_sess.close()
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Ваш ответ успешно засчитан!")


async def registration(vk, event):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.user_id == event['from_id']).first()
    if user:
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Вы уже зарегистрированы")
        return
    user = User(user_id=event['from_id'])
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()
    await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Ваша регистрация прошла успешно")


async def to_give_post(vk, event):
    data = event['text'].split()
    if len(data) != 3:
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Используйте !дать_дол <название "
                                                                              "должности> @<user>")
    elif data[1].lower() not in posts:
        await vk.messages_send(peer_id=event['peer_id'], random_id=0, message="Такой должности нет, вот какие есть:\n"
                                                                              f"{', '.join(posts)}")
    else:
        user_id = get_user_id(data)
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.user_id == user_id).first()
        user.post = posts.index(data[1].lower())
        db_sess.commit()
        db_sess.close()
        user_info = await vk.users_get(user_id=user_id)
        await vk.messages_send(peer_id=event['peer_id'], random_id=0,
                               message=f"Пользователь {user_info[0]['first_name']} {user_info[0]['last_name']} получил "
                                       f"звание {data[1].lower()}")


async def start_bot():
    session = vkreal.VkApi(token=token)
    vk = session.api_context()
    longpool = vkreal.VkBotLongPoll(session, "222158127")
    async for event in longpool.listen():
        print(event)
        if event['type'] != 'message_new':
            continue
        else:
            event = event['object']['message']
            if event['text'] in ['/start', 'Начать']:
                loop.create_task(hello(vk, event))
            if event['text'].startswith("!связаться"):
                loop.create_task(get_request(vk, event))
            if event['text'] == "!регистрация":
                loop.create_task(registration(vk, event))
            if check_admin(event):
                if event['text'].startswith("!ответ"):
                    loop.create_task(answer_on_request(vk, event))
                if check_super_admin(event):
                    if event['text'].startswith('!дать_дол'):
                        loop.create_task(to_give_post(vk, event))


loop = asyncio.new_event_loop()
loop.create_task(start_bot())
loop.run_forever()
