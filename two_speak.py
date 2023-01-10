# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# To change this template file, choose Tools | Templates
# and open the template in the editor.n

# to test calling smile and eye brink, by using armature pose bone to drive key shapes 

import aud
import bge
from bge import texture
from bge import render as R
from bge import logic as G 
import utilities as U
import json

CONVERSE_MODE_STOP=0
CONVERSE_MODE_PLAY=1

CONVERSE_MARKER_START = 0
CONVERSE_MARKER_END = 1

MENU_MODE_PLAY_STOP = 0
MENU_MODE_PLAY_START = 1
MENU_MODE_PLAY_PAUSE = 2
MENU_MODE_PLAY_RESUME = 3

G.kick_start = 0
# play around with access to actuator

# alan = Person('objAction': 'alanAction', 'layer':0, 'playByParent':False, 'speakerObj':objects['alan'])

        

# read me:
# M20221027 two_speak.py
# author: ct
# objective:  to run a scene with multiple lines spoken by two speakers
#
# try to replicate oop.blend in game engine book by mike pan 
#
# steps to buy the logic bricks to run modules with two_speak.py
# init_speak() for initial controller and speak() for speak action
# use an always sensor to run a controller to run def init_speak() in high priority
# and use another always sensor to run  script in every frame

# dictionary for each speaker name: [action name, layer number]
#  dictionary for each line number : [speaker obj name, waiting obj name, start frame, end frame, sound file name]

# create a class of conversation, so that we could ask to speak, to pause, to restart with the instance

class Converse:
    def __init__(self, dopeList):
        self.dopeList = dopeList
        #self.speakerDict = speakerDict
        self.debug = False
        self.play_control = False  # if set it means conversation is enabled
        self.complete_status = True
        self.time_delay = 5   # set time frames between each replay
        self.time_from_endCheck = 0  # set variables to register 
        self.mode = CONVERSE_MODE_STOP
        self.pause_mode = False
        self.marker = CONVERSE_MARKER_START
        
        ##### to allow render image on the plane
        if False:
            self.scene = G.getCurrentScene()
            self.rendercam = self.scene.objects['renderCamera']
            renderplane = self.scene.objects['renderplane']
            G.overlayTex = texture.Texture(renderplane, 0, 0)
            G.overlayTex.source = texture.ImageRender(self.scene,self.rendercam)
        
    def render_overlay(self):
        # set rendercam as active cam
        camBackup = self.scene.active_camera
        self.scene.active_camera = self.rendercam
        
        # render overlay camera to renderplane texture
        G.overlayTex.refresh(True)
        self.scene.active_camera = camBackup
        
        
        
        
    def switch_scene(self, cont, add_coll, remove_coll=None):
        #cont = G.getCurrentController()
        #owner = cont.owner
        #scene = G.getCurrentScene()
        #rendercam = scene.objects["renderCamera"]
        
        #objects = scene.objects

        # objects obtain this way belong to class KX_GameObject, not bpy.data.objects
        #senLeft = cont.sensors['s_LeftKey']
        
        
        if remove_coll is not None:
            actu_remove = cont.actuators[remove_coll]
            cont.activate(actu_remove)
        
        actu_add = cont.actuators[add_coll]
        cont.activate(actu_add)
        
        
        
    def endCheck(self,cont):
        #scene = G.getCurrentScene()
        #objects = scene.objects
        # if each of the line is spoken and is no longer playing then it is true
        # if add up to the status with AND, all line True will end up status returned as True
        # meaning the conversation is completed. 
        status = True
        for line in self.dopeList:
            #speaker = line['speaker']
            #speakerLayer = speaker.layer
            #speakerObj = speaker.speakerObj
            #status = status and (line['spoken'] and not speakerObj.isPlayingAction(speakerLayer))
            status = status and line['completed']
        if status: print('the conversation is completed!! ', status)     
        return status        
    
    def toStopSpeak(self, cont):
        self.toReset(cont)
    
    def print_state(self, cont):
        
        for line in self.dopeList:    # loop for each line

            speaker = line['speaker']    # for each line get the speaker and who it is waiting for
            speakerLayer = speaker.layer
            speakerObj = speaker.speakerObj
            print('line: %s, \n, speaker %s, which playing action state is: %s at frame: %3d has line_spoken: %s' % \
                    (line, speakerObj, speakerObj.isPlayingAction(speakerLayer), speakerObj.getActionFrame(speakerLayer), line['spoken']))
             
            
            
    
    def toReset(self, cont):
        # need also to bring the action Frame of individual object back to frame 1

        if self.debug: print("running toReset()")
        
        for line in self.dopeList:    # loop for each line

            speaker = line['speaker']    # for each line get the speaker and who it is waiting for
            speakerLayer = speaker.layer
            speakerObj = speaker.speakerObj
            if self.debug:
                print('line: %s, \n, speaker %s, which playing action state is: %s at frame: %3d has line_spoken: %s' % \
                    (line, speakerObj, speakerObj.isPlayingAction(speakerLayer), speakerObj.getActionFrame(speakerLayer), line['spoken']))
             
            
            #speakerObj.setActionFrame(0)
            speakerObj.stopAction(speakerLayer)
            self.marker = CONVERSE_MARKER_START
            line['spoken']=False
            line['completed']=False
            
        
    
    def toPlay(self, cont):
        print('running toPlay')
        for line in self.dopeList:    # loop for each line
            if line['spoken']:
                next
            else:    
                speaker = line['speaker']    # for each line get the speaker and who it is waiting for
                waitFor = line['waitFor']

                speakerLayer = speaker.layer
                speakerObj = speaker.speakerObj
                speakerAction = speaker.objAction
                soundFileName = line['soundFileName']

                if not (waitFor == None):
                    waitForLayer = waitFor.layer
                    waitForObj = waitFor.speakerObj
                    endRange = range(line['waitForFrame'][0],line['waitForFrame'][1]) 

                # speak out if the line is not start spoken and the object is not speaking anything at the same time
                # the latter condition is added to make sure the speaker is not speaking cue as well.
                frame = speakerObj.getActionFrame(speakerLayer)
                if frame == line['endFrame']:  line['completed'] = True


                if not (line['spoken'] or speakerObj.isPlayingAction(speakerLayer)):
                    if self.debug:
                        print('line: %s, \nSpeaker %s, who playing status is: %3d, running frame: %3d.' % \
                           (line, speakerObj, speakerObj.isPlayingAction(speakerLayer), \
                           speakerObj.getActionFrame(speakerLayer)))

                        if (waitFor == None):
                                print('')

                                print('waiting for: %s which playing status is: %3d, running frame: %3d, test within endRange %d.' % \
                                   (waitForObj, waitForObj.isPlayingAction(waitForLayer), \
                                    waitForObj.getActionFrame(waitForLayer), \
                                    waitForObj.getActionFrame(waitForLayer)in endRange))


                    if waitFor == None or waitForObj.getActionFrame(waitForLayer)in endRange:  # no need to wait for d01 if it has not been spoken
                        speakerObj.playAction(speakerAction,line['startFrame'],line['endFrame'], layer = speakerLayer)
                        if soundFileName: speaker.playSoundV1(soundFileName, G.soundPathName)
                        line['spoken']=True   # set status as spoken, that is commence speaking so that in next frame the action will not be executed again.
                        if line['line'] == 'd01':   self.marker = CONVERSE_MARKER_START

                # just check for whether it is end of conversation        
                if line['line'] == 'd99' and line['spoken'] and not speakerObj.isPlayingAction(speakerLayer): 
                    print('line d99 is spoken and not playing')
                    self.marker = CONVERSE_MARKER_END
                    # G.converse.mode == CONVERSE_MODE_STOP
        
        
        
                
    def toPlay_backup(self, cont):
        print('running toPlay')
        for line in self.dopeList:    # loop for each line

            speaker = line['speaker']    # for each line get the speaker and who it is waiting for
            waitFor = line['waitFor']
            
            speakerLayer = speaker.layer
            speakerObj = speaker.speakerObj
            speakerAction = speaker.objAction
            soundFileName = line['soundFileName']

            if not (waitFor == None):
                waitForLayer = waitFor.layer
                waitForObj = waitFor.speakerObj
                endRange = range(line['waitForFrame'][0],line['waitForFrame'][1]) 
            
            # speak out if the line is not start spoken and the object is not speaking anything at the same time
            # the latter condition is added to make sure the speaker is not speaking cue as well.
            frame = speakerObj.getActionFrame(speakerLayer)
            if frame == line['endFrame']:  line['completed'] = True
            
            
            if not (line['spoken'] or speakerObj.isPlayingAction(speakerLayer)):
                if self.debug:
                    print('line: %s, \nSpeaker %s, who playing status is: %3d, running frame: %3d.' % \
                       (line, speakerObj, speakerObj.isPlayingAction(speakerLayer), \
                       speakerObj.getActionFrame(speakerLayer)))
                    
                    if (waitFor == None):
                            print('')

                            print('waiting for: %s which playing status is: %3d, running frame: %3d, test within endRange %d.' % \
                               (waitForObj, waitForObj.isPlayingAction(waitForLayer), \
                                waitForObj.getActionFrame(waitForLayer), \
                                waitForObj.getActionFrame(waitForLayer)in endRange))

                
                if waitFor == None or waitForObj.getActionFrame(waitForLayer)in endRange:  # no need to wait for d01 if it has not been spoken
                    speakerObj.playAction(speakerAction,line['startFrame'],line['endFrame'], layer = speakerLayer)
                    if soundFileName: speaker.playSoundV1(soundFileName, G.soundPathName)
                    line['spoken']=True   # set status as spoken, that is commence speaking so that in next frame the action will not be executed again.
                    if line['line'] == 'd01':   self.marker = CONVERSE_MARKER_START
            
            # just check for whether it is end of conversation        
            if line['line'] == 'd99' and line['spoken'] and not speakerObj.isPlayingAction(speakerLayer): 
                print('line d99 is spoken and not playing')
                self.marker = CONVERSE_MARKER_END
                # G.converse.mode == CONVERSE_MODE_STOP
def read_converses():
    # load dopeList from json file
    file_path = 'C:\\Users\\Think\\OneDrive\\Documents\\blender_working\\proj_word_naming\\prod\\3D\\edit\\scenes\\cup_of_tea'
    with open(file_path+'\\' + 'converses.json', 'r') as f:
        data = json.load(f)
        #print(data)
    G.converses=[]
    for i in data['converses']:
        print('name_object: \n', {i['name_object']})
        for line in i['dope_list']:
            print('line: ', line)
        G.converses.append(i)    
    print('G.converse: {G.converses}')
    f.close()
            
def initSpeak(cont):
    # trigger by an always sensor, execute once only with high priority
    #
    # fileInfo for information only no coding effect
    owner = cont.owner
    scene = G.getCurrentScene()  
    objects = scene.objects
    R.showMouse(True)
    camList = scene.cameras
    menu_camera = camList['menu_camera']
    render_camera = camList['renderCamera']
    #scene.active_camera = menu_camera
    scene.active_camera = render_camera
    G.source = []    
    
    fileInfo ={0:'playingAssetReuseV4d.blend', 1:'playingAssetReuseV4d.blend'}  # key: value = scene: blender file name
         
    alan = U.Person(objAction = 'alanAction', layer =0, playByParent = False, name = 'alan')  
    nina = U.Person(objAction = 'ninaAction', layer =1, playByParent = False, name = 'nina')  
    renderCamera = U.Person(objAction = 'renderCameraAction', layer =3, name = 'menu_camera')  
    
    read_converses()

    name_object = U.Person(objAction = 'cup_of_teaAction', layer =2, name = 'cup_of_tea')
    dopeList =[{'line': 'd01', 'speaker': alan, 'startFrame': 1, 'endFrame':  89, 'soundFileName': "d01_INV_CAR.wav", 'waitFor':None, 'waitForFrame':(1,20),  'spoken':False, 'completed':False},
                {'line': 'p01', 'speaker': name_object, 'startFrame': 1, 'endFrame':  10, 'soundFileName': None, 'waitFor':None, 'waitForFrame':(1,20),'spoken':False, 'completed':False},
                {'line': 'd01_aft', 'speaker': alan, 'startFrame': 90, 'endFrame':  237, 'soundFileName': None, 'waitFor':alan, 'waitForFrame':(80,89),  'spoken':False, 'completed':False},
                {'line': 'd04', 'speaker': alan, 'startFrame': 238, 'endFrame':  318, 'soundFileName': "d04_INV_CAR.wav", 'waitFor':nina, 'waitForFrame':(230,239),'spoken':False, 'completed':False},
                {'line': 'd06', 'speaker': alan, 'startFrame': 350, 'endFrame':  370, 'soundFileName': "d06_INV_CAR.wav", 'waitFor':nina, 'waitForFrame':(340,346),'spoken':False, 'completed':False},
                {'line': 'd02', 'speaker': nina, 'startFrame': 90, 'endFrame':  158, 'soundFileName': "d02_CAR_CAR.wav", 'waitFor':alan, 'waitForFrame':(80,90), 'spoken':False, 'completed':False},
                {'line': 'd03', 'speaker': nina, 'startFrame': 160, 'endFrame':  238, 'soundFileName': "d03_CAR_INV.wav", 'waitFor':nina, 'waitForFrame':(150,159),'spoken':False, 'completed':False},
                {'line': 'd05', 'speaker': nina, 'startFrame': 318, 'endFrame':  345, 'soundFileName': "d05_CAR_INV.wav",'waitFor':alan, 'waitForFrame':(310,319), 'spoken':False, 'completed':False},
                {'line': 'p02', 'speaker': name_object, 'startFrame': 317, 'endFrame':  330, 'soundFileName': None, 'waitFor':nina, 'waitForFrame':(318,345),'spoken':False, 'completed':False},
                {'line': 'd99', 'speaker': nina, 'startFrame': 380, 'endFrame':  470, 'soundFileName': "d07_CAR_TAR.wav", 'waitFor':alan, 'waitForFrame':(360,371),'spoken':False, 'completed':False}]

    G.converse = Converse(dopeList)  
    
    
    G.soundPathName = ('C:\\Users\\Think\\OneDrive\\Documents\\blender_working\\proj_word_naming\\prod\\3D\\assets\\sound\\conversationFromWordTalk')
    print('G.converse', G.converse, 'dir(converse)', dir(G.converse))

#   set up arrow menu.  Hence no need to use another always sensor and controller for init_menu

    # initialize the menu with standard items of arrowPlay, arrowStop, arrowForward and arrowBack
    
    
    #U.initMenu(cont)
    
    # add an menu object (i.e. alan_menu and nina_menu) to the standard items
    # when the mouse manuevre alan's material on head or nina's body it activate the relevant button
    # the value name need to be the name of the object in blender
    G.alan_menu = U.Menu_button(objAction = 'alanAction', layer =0, playByParent = False, \
            name = 'alan', activated=False, start_frame= 470, end_frame =543, soundFileName='d08_INV_TAR.wav')  
    
    #alanMouseDict = { 's_mouseLeft': G.defaultMouseLeftSensor, 's_mouseOver':'s_alan_mouseOver', 'menu_object': G.alan_menu}
    alanMouseDict = { 's_mouseOver':'s_alan_mouseOver.001', 'menu_object': G.alan_menu, 'menu_camera': menu_camera}

    G.nina_menu = U.Menu_button(objAction = 'ninaAction', layer =1, playByParent = False, \
            name = 'nina', activated=False, start_frame= 543, end_frame =664, soundFileName='d09_CAR_TAR.wav')  
    
    ninaMouseDict = { 's_mouseOver':'s_nina_mouseOver.001', 'menu_object': G.nina_menu, 'menu_camera': menu_camera}

    # add mouse over alan and nina as feature to activate cue
    G.arrow_menu_mouse.addDict('alan', alanMouseDict)
    G.arrow_menu_mouse.addDict('nina', ninaMouseDict)
    
    #add key J and K as to activate cue for alan and nina as well
    alanKeyDict = {'assignKey': bge.events.JKEY, 'menu_object' : G.alan_menu}
    G.arrow_menu_key.addDict('alan', alanKeyDict)
    ninaKeyDict = {'assignKey': bge.events.KKEY, 'menu_object' : G.nina_menu}
    G.arrow_menu_key.addDict('nina', ninaKeyDict)
 

 
 
def render_background(cont, pic_mat, index=None):

    # get current scene
    scene = G.getCurrentScene()

    # get list of objects in scene
    objList = scene.objects

    # get object named Plane
    obj = objList["background_plane"]
    
    # check to see if the render has been created
    if "object_texture" in obj:
        print('yes, object_texture has been created in obj', obj)

        # get texture
        object_texture  = obj["object_texture"]

        if index is None:
            # update the texture
            # object_texture.refresh(False)
            pass
            #object_texture.refresh(False)  # try to refresh every frames
        
        else:
            object_texture.source = G.source[index]
            object_texture.refresh(True)

    # if the mirror wasn't created
    else:
            
            # The name of object material being used for the mirror
            # I named the material Reflect
            #mat = "MAReflect"   remember to add prefix for material (MA) or image (IM)
            
            mat = pic_mat
            print('mat', pic_mat)
            # get the mirror material ID
            matID = bge.texture.materialID(obj, mat)
            print ('material obj: ',obj, 'and mat ID', matID)
            
            # get texture being replaced
            # texture I'm using is in 1st Channel
            texChannel = 0

            # create a new source with an external image
            
            G.source.append(texture.ImageFFmpeg(G.expandPath("//sleepz.jpg")))

            G.source.append(texture.ImageFFmpeg(G.expandPath("//dundeeHighStreetScene.jpg")))

            G.source.append(texture.ImageFFmpeg(G.expandPath("//james_hutton.jpg")))
            
            # create a the texture object
            #object_texture = bge.texture.Texture(obj, matID, texChannel)
            object_texture = bge.texture.Texture(obj, matID)
            object_texture.source = G.source[0]
            
            # save mirror as an object variable
            obj["object_texture"] = object_texture
            
            
            print('calling to create texture', object_texture)
            object_texture.refresh(True)
            
def changeTexture(cont, index):
    
    scene = G.getCurrentScene()

    # get list of objects in scene
    objList = scene.objects

    # get object named Plane
    obj = objList["background_plane"]
    
        # get current scene
    
    # update/replace the texture
    obj["texture"].source = G.source[index]
    #logic.texture.refresh(False)
    G.background_texture.refresh(False)



def removeTexture(cont):
    # get current scene
    scene = bge.logic.getCurrentScene()

    # get list of objects in scene
    objList = scene.objects

    # get object named Plane
    obj = objList["background_plane"]

    try:
        del obj['object_texture']
    except:
        pass

        

def speak(cont):
    # retrieve arrowPlay.activated to play, arrowStop.activated to ?, arrowPlay.pause_mode 
    #scene = G.getCurrentScene()  
    #cont = G.getCurrentController()
    
    def cb_play():
        def _inner():
            #G.converse.toPlay(cont)
            print('playing call back - cb_play')
        return _inner
    
    def cb_pause():
        def _inner():
            #cont.activate(cont.actuators['a_coll_suspend_cup_of_tea'])
            print('pausing call back')
        return _inner
    
    def cb_resume():
        def _inner():
            #cont.activate(cont.actuators['a_coll_resume_cup_of_tea'])
            print('resuming call back')
        return _inner

    
    def cb_stop():
        def _inner():
            G.converse.toReset(cont)
            #cont.activate(cont.actuators['a_coll_suspend_cup_of_tea'])
            print('stop call back')
        return _inner

    def cb_backward():
        def _inner():
            render_background(cont, 'MApic_mat', 1)
            print('backward call back')
        return _inner


    def cb_forward():
        def _inner():
            render_background(cont, 'MApic_mat', 2)
            print('forward call forward')
        return _inner


    f1 = cb_play()
    f2 = cb_pause()
    f4 = cb_stop()
    f3 = cb_resume()
    f5 = cb_backward()
    f6 = cb_forward()
    
    if G.kick_start == 0:
        U.initMenu(cont)
        initSpeak(cont)
        render_background(cont, 'MApic_mat')
        cont.activate(cont.actuators['a_coll_add_cup_of_tea'])

        G.kick_start += 1
    
    render_background(cont, 'MApic_mat')
    
    if G.flag_mouse:  G.arrow_menu_mouse.update(f1, f2, f3, f4, f5, f6)
        
    if G.flag_key: G.arrow_menu_key.update(f1, f2, f3, f4, f5, f6)
    
    if (G.arrowPlay.play_mode == MENU_MODE_PLAY_START or G.arrowPlay.play_mode == MENU_MODE_PLAY_RESUME) \
        and not G.converse.marker == CONVERSE_MARKER_END:
        G.converse.toPlay(cont)
    
    
        
    



