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
import mimetypes

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
    
    # [{'objAction' : 'alanAction', 'layer' :0, 'playByParent' : False, 'name' : 'alan'},
    def __init__(self, dopeList, charList, background_pic, display_cube_pic):
        self.charList = charList
        self.dopeList = dopeList
        self.background_pic = background_pic
        self.display_cube_pic = display_cube_pic
    
        self.debug = False
        self.play_control = False  # if set it means conversation is enabled
        self.complete_status = True
        self.time_delay = 5   # set time frames between each replay
        self.time_from_endCheck = 0  # set variables to register 
        self.mode = CONVERSE_MODE_STOP
        self.pause_mode = False
        self.marker = CONVERSE_MARKER_START
    
    
        char ={}
        for i in self.charList:
            print(f'i in self.charList: {i}')
            
            obj = U.Person(objAction = i['objAction'], layer = i['layer'], \
                  playByParent = i['playByParent'], name = i['name'])
            char[i['name']]=obj
        
        for line in self.dopeList:  # add items of objects to the list in which the speaker_name and the wait_for_name should be  in the char dict 
            line['speaker'] = char[line['speaker_name']]
      
            line['wait_for'] = None if line['wait_for_name'] is None else char[line['wait_for_name']]
            

        
        
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
                wait_for = line['wait_for']

                speakerLayer = speaker.layer
                speakerObj = speaker.speakerObj
                speakerAction = speaker.objAction
                soundFileName = line['soundFileName']

                if not (wait_for == None):
                    wait_forLayer = wait_for.layer
                    wait_forObj = wait_for.speakerObj
                    endRange = range(line['wait_for_frame']['low'],line['wait_for_frame']['high']) 

                # speak out if the line is not start spoken and the object is not speaking anything at the same time
                # the latter condition is added to make sure the speaker is not speaking cue as well.
                frame = speakerObj.getActionFrame(speakerLayer)
                if frame == line['endFrame']:  line['completed'] = True


                if not (line['spoken'] or speakerObj.isPlayingAction(speakerLayer)):
                    if self.debug:
                        print('line: %s, \nSpeaker %s, who playing status is: %3d, running frame: %3d.' % \
                           (line, speakerObj, speakerObj.isPlayingAction(speakerLayer), \
                           speakerObj.getActionFrame(speakerLayer)))

                        if (wait_for == None):
                                print('')

                                print('waiting for: %s which playing status is: %3d, running frame: %3d, test within endRange %d.' % \
                                   (wait_forObj, wait_forObj.isPlayingAction(wait_forLayer), \
                                    wait_forObj.getActionFrame(wait_forLayer), \
                                    wait_forObj.getActionFrame(wait_forLayer)in endRange))


                    if wait_for == None or wait_forObj.getActionFrame(wait_forLayer)in endRange:  # no need to wait for d01 if it has not been spoken
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
    #C:\Users\Think\OneDrive\Documents\blender_working\proj_word_naming\nbupbge\src\scripts
    file_path = 'C:\\Users\\Think\\OneDrive\\Documents\\blender_working\\proj_word_naming\\nbupbge\\src\\scripts'
    with open(file_path+'\\' + 'converses_v1.json', 'r') as f:
        data = json.load(f)
    
    G.background_pic_dict = data["background_pic_dict"]
    mimetypes.init()
    G.background_pic_type_dict = {}
    
    for x, y in G.background_pic_dict.items():
        file_name = G.expandPath("//"+y)
        mimestart = mimetypes.guess_type(file_name)[0]
        mimestart = mimestart.split('/')[0]
        G.background_pic_type_dict[x] = mimestart
    
    G.converses=[]
    for i in data['converses']:  # each i is a dictionary containing pairs of '_comment', 'name_object', and 'dope_list'
        print(f'i in data["converses"]: \n{i}')
        print(f' -- comment: \n {i["_comment"]} \
        \n   charList: \n{i["charList"]} \
        \n   dope_list: \n{i["dopeList"]}  \
        ')
        
        G.converses.append(Converse(i["dopeList"],i["charList"], i["background_pic"], i["display_cube_pic"])) 
        
    print(f'G.converses: {G.converses}')
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
    G.background_pic_source = {}
  
    
    fileInfo ={0:'playingAssetReuseV4d.blend', 1:'playingAssetReuseV4d.blend'}  # key: value = scene: blender file name
         
   
    read_converses()
    # register the counter of the converse to run
    G.converse_seq= 0
    G.converse = G.converses[G.converse_seq]
    
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
 
def render_background(cont, obj_name, pic_mat, pic_key=None, video=False):

    # get current scene
    scene = G.getCurrentScene()

    # get list of objects in scene
    objList = scene.objects

    # get object named Plane
    #obj = objList["background_plane"]
    obj = objList[obj_name]
    
    # check to see if the render has been created
    if "object_texture" in obj:
        print('yes, object_texture has been created in obj', obj)

        # get texture
        object_texture  = obj["object_texture"]

        if pic_key is None:
            # update the texture
            # object_texture.refresh(False)
            pass
            #object_texture.refresh(False)  # try to refresh every frames
        
        else:
            #object_texture.source = G.source[pic_key]
            object_texture.source = G.background_pic_source[pic_key]
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
            # x is the picture name, y is the file name of the file
            # now the dict G.background_pic_source contain the pair of x, texture containing the file image
            #for x, y in G.background_pic_dict.items():
            #    G.background_pic_source[x] = texture.ImageFFmpeg(G.expandPath("//"+y))
            #  the above is done in init
            # create a the texture object
            #object_texture = bge.texture.Texture(obj, matID, texChannel)
            object_texture = bge.texture.Texture(obj, matID)
            #object_texture.source = G.source[0]
            #object_texture.source = G.background_pic_source[G.converse.background_pic]
            object_texture.source = G.background_pic_source[pic_key]
            # save mirror as an object variable
            obj["object_texture"] = object_texture
            
            
            print('calling to create texture', object_texture)
            object_texture.refresh(True)
 
 
 
def render_background_backup(cont, obj_name, pic_mat, pic_key=None):

    # get current scene
    scene = G.getCurrentScene()

    # get list of objects in scene
    objList = scene.objects

    # get object named Plane
    #obj = objList["background_plane"]
    obj = objList[obj_name]
    
    # check to see if the render has been created
    if "object_texture" in obj:
        print('yes, object_texture has been created in obj', obj)

        # get texture
        object_texture  = obj["object_texture"]

        if pic_key is None:
            # update the texture
            # object_texture.refresh(False)
            pass
            #object_texture.refresh(False)  # try to refresh every frames
        
        else:
            #object_texture.source = G.source[pic_key]
            object_texture.source = G.background_pic_source[pic_key]
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
            # x is the picture name, y is the file name of the file
            # now the dict G.background_pic_source contain the pair of x, texture containing the file image
            for x, y in G.background_pic_dict.items():
                G.background_pic_source[x] = texture.ImageFFmpeg(G.expandPath("//"+y))
            
            # create a the texture object
            #object_texture = bge.texture.Texture(obj, matID, texChannel)
            object_texture = bge.texture.Texture(obj, matID)
            #object_texture.source = G.source[0]
            object_texture.source = G.background_pic_source[G.converse.background_pic]
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
            #render_background(cont, 'MApic_mat', 1)
            
            G.converse_seq = (G.converse_seq -1) % len(G.converses)
            G.converse = G.converses[G.converse_seq]
            render_background(cont, 'background_plane', 'MApic_mat', G.converse.background_pic)
            render_background(cont, 'display_cube', 'MAdisplay_cube_front_mat', G.converse.display_cube_pic)
            print('backward call back')
            print(f' background_pic: \n{G.converse.background_pic} \
            \n   charList: \n{G.converse.charList} \
            \n   dopelist: \n{G.converse.dopeList}  \
            ')

        return _inner


    def cb_forward():
        def _inner():
            #render_background(cont, 'MApic_mat', 2)
            
            G.converse_seq = (G.converse_seq +1) % len(G.converses)
            G.converse = G.converses[G.converse_seq]
            render_background(cont, 'background_plane', 'MApic_mat', G.converse.background_pic)
            render_background(cont, 'display_cube', 'MAdisplay_cube_front_mat', G.converse.display_cube_pic)
            print('forward call forward')
            print(f' background_pic: \n{G.converse.background_pic} \
            \n   charList: \n{G.converse.charList} \
            \n   dopelist: \n{G.converse.dopeList} \
            ')

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
        
        for x, y in G.background_pic_dict.items():
            G.background_pic_source[x] = texture.ImageFFmpeg(G.expandPath("//"+y))
            
        render_background(cont, 'background_plane', 'MApic_mat', G.converse.background_pic)
        render_background(cont, 'display_cube', 'MAdisplay_cube_front_mat', G.converse.display_cube_pic)
        
        #render_background(cont, 'background_plane', 'MApic_mat')
        cont.activate(cont.actuators['a_coll_add_cup_of_tea'])

        G.kick_start += 1
    
    render_background(cont, 'background_plane', 'MApic_mat')
    render_background(cont, 'display_cube', 'MAdisplay_cube_front_mat')
    
    if G.flag_mouse:  G.arrow_menu_mouse.update(f1, f2, f3, f4, f5, f6)
        
    if G.flag_key: G.arrow_menu_key.update(f1, f2, f3, f4, f5, f6)
    
    if (G.arrowPlay.play_mode == MENU_MODE_PLAY_START or G.arrowPlay.play_mode == MENU_MODE_PLAY_RESUME) \
        and not G.converse.marker == CONVERSE_MARKER_END:
        G.converse.toPlay(cont)
    
    
        
    



