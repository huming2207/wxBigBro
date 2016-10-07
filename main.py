import itchat, time, sys, os
import settings
from gmail import Message
from gmail import GMail


gmail = GMail(settings.username_str, settings.password_str)
atJudgement = '@胡铭'

# Register the message type
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def get_msg(msg):
    writeContent(msg['ActualNickName'], msg['Content'])
    # “IsAt” method sometimes may be broken, so use this instead.
    if atJudgement in str(msg['Content']):
        print("Damn I have to reply again! Someone @ me again!")
        itchat.send('胡铭的小群辉: Got message: \"%s\", from \"%s\"' % (msg['Content'], msg['ActualNickName']), msg['FromUserName'])

@itchat.msg_register([itchat.content.ATTACHMENT, itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.VIDEO], isGroupChat=True)
def download_files(msg):
    writeBinary(str(msg['ActualNickName']), msg)
    

def main():    
    login()
    itchat.run()

def login():
    uuid = open_QR()
    waitForConfirm = False
    while 1:
        status = itchat.check_login(uuid)
        time.sleep(0.5)
        if status == '200':
            break
        elif status == '201':
            if waitForConfirm:
                output_info('Please press confirm')
                waitForConfirm = False
        elif status == '408':
            output_info('Reloading QR Code')
            uuid = open_QR()
            waitForConfirm = False
    userInfo = itchat.web_init()
    itchat.web_init()
    itchat.show_mobile_login()
    itchat.get_friends(True)
    output_info('Login successfully as %s'%userInfo['NickName'])
    itchat.start_receiving()

def output_info(msg):
    print('[INFO] %s' % msg)

def open_QR():
    for get_count in range(10):
        output_info('Getting uuid')
        uuid = itchat.get_QRuuid()
        while uuid is None: uuid = itchat.get_QRuuid();time.sleep(1)
        output_info('Getting QR Code')
        if itchat.get_QR(uuid): 

            # WARNING:  In this line we cannot send any words like "scan this QR code please"
            #           otherwise the Email service provider may suspend your account as they 
            #           believe you are sending spam mail!!!
            message = Message('Server notification: WX RELOGIN INFO', settings.dest_email_str, text='Hey, I\'m your server!', attachments=['QR.jpg'])    
            gmail.send(message)
            
            break
        elif get_count >= 9:
            output_info('Failed to get QR Code, please restart the program')
            sys.exit()
    output_info('Please scan the QR Code')
    return uuid


def writeContent(user_nickname, content):
    if not os.path.exists(settings.base_path + user_nickname):
        os.makedirs(settings.base_path + user_nickname)
    
    current_time = str(int(time.time()))
    file_pathname = settings.base_path + user_nickname + '/' + current_time + '.txt'
    output_info('Grabbed one text content, saved to ' + file_pathname)
    filehandler = open(file_pathname, mode='w')
    filehandler.writelines(content)
    filehandler.close()

def writeBinary(user_nickname, message):
    if not os.path.exists(settings.base_path + user_nickname):
        os.makedirs(settings.base_path + user_nickname)

    current_time = str(int(time.time()))
    file_pathname = str(settings.base_path + user_nickname + '/' + current_time + "-" + message['FileName'])
    output_info('Grabbed one unknown binary content, saved to ' + file_pathname)
    message['Text'](file_pathname)

if __name__ == "__main__": main()