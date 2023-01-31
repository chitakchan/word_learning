# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
# utilities including the use of mouse to select a menu of four arrows up/down and left/right
import bge
import aud
from bge import logic as G
import random
#import two_speak
# to set up the logic brick
# 1.  one always sensor to run initMenu, marked with high priority
#       initMenu set up the global dictionary for mouse and key for each button 
# 2. another always sensor at pulse mode to run ArrowMenu at every frame, 
#       in arrowMenu, two objects of ArrowMenuMouse class and another of ArrowMenuKey class 
#       are created, and their status are updated at every frame.
# 3.  




# development logs
# because it replace the logic block of keyboard it will need to add a logic block of always
# enabling Pulse mode to trigger the controller
# add mouse 02/09/2022
# but perhaps easier to use logic brick for mouse, as it needs certain transformation (ray casting)
# to detect mouse over and programming may be a bit complicated
# work on 10.9.2022 on cdMenu.blend


# 
#    arrowPlay = Menu_button(objAction = 'arrowAction', layer =3, playByParent = False, name = 'arrowPlay', activated=False, start_frame= =1, end_frame =16)  


MENU_MODE_STOP = 0

MENU_MODE_PLAY_STOP = 0
MENU_MODE_PLAY_START = 1
MENU_MODE_PLAY_PAUSE = 2
MENU_MODE_PLAY_RESUME = 3

class Person:
    def __init__(self, name, objAction, layer, playByParent=False):
        scene = G.getCurrentScene()  
        objects = scene.objects
        self.name = name
        self.objAction = objAction
        self.layer = layer
        # you can access to attributes within the bpy.data with blenderObject.data
        #self.speakerObj_data = speakerObj.blenderObject.data
        #self.gameObj['frame'] = 0
        self.playByParent=playByParent
        if playByParent:
            self.speakerObj = objects[name].parent
        else:
            self.speakerObj = objects[name]
        self.obj = objects[name]
            
    def get_game_obj(self):
        return self.obj

    def playSoundV1(self, fileName, pathName):
        #import aud
        file = pathName + '\\'+ fileName
        device = aud.Device()
        # load sound file (it can be a video file with audio)
        sound = aud.Sound(file)

        # play the audio, this return a handle to control play/pause
        handle = device.play(sound)
        # if the audio is not too big and will be used often you can buffer it
        #sound_buffered = aud.Sound.cache(sound)
        #handle_buffered = device.play(sound_buffered)

        # stop the sounds (otherwise they play until their ends)
        #handle.stop()
        #handle_buffered.stop()

class Menu_button(Person):
    # a sub class of Person specific for menu button objects
    #
    def __init__(self, name, objAction, start_frame, end_frame, layer, playByParent = False, activated = False, \
    soundFileName = ""):
        super().__init__(name, objAction, layer, playByParent)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self._activated = activated
        self.soundFileName = soundFileName
        self.status = G.KX_INPUT_NONE
        self.count = False
        
    @property
    def activated(self):
        return self._activated
    
    @activated.setter
    def activated(self, value):
        tracking_n = random.random()
        
        self.count = not self.count   # swap count so that the setter only work in interval
            
        if G.skip_count or self.count:

            print('-',tracking_n , '** running activated.setter **** self and value and track no ***', \
                    self, ',', value )
            if value: 
                self.playAction()  # if it is True
                self._activated = True

    @activated.deleter
    def activated(self):   # call by del obj.activated
        
        del self._activated
        
    def deactivated(self):
        if self._activated:
            print('deactivate the menu button', self)
            self._activated = False
            
    
    def playAction(self):
        #key_value = self.mediaDict[key]
        menu_object = self

        arrowActionName = menu_object.objAction
        startFrame = menu_object.start_frame
        endFrame = menu_object.end_frame
        layer =  menu_object.layer
        soundFileName = menu_object.soundFileName
        playingObj = menu_object.speakerObj
        
        
        print('activated key: ', self)
        print('-- is activated to the object playingObj', playingObj, ' with action: ', arrowActionName)

        #if arrowActionName and not playingObj.isPlayingAction(layer) and G.play_action_flag:
        if arrowActionName and G.play_action_flag:
            playingObj.playAction(arrowActionName, endFrame, startFrame, priority=0, \
            layer=layer)
#            play_mode = G.KX_ACTION_MODE_PING_PONG dont work, it loop endlessly.
            # if soundFileName: self.playSoundV1(soundFileName, G.soundPathName)
            if soundFileName: menu_object.playSoundV1(soundFileName, G.soundPathName)
                

        
        
        
class Menu_button_play(Menu_button):
    # a sub class of Person specific for play button which contain dual action:  play and pause
    #
    def __init__(self, name, objAction, start_frame, end_frame, layer, playByParent = False, activated = False, \
        soundFileName = "", play_colourAction=None, pause_colourAction=None):
        super().__init__(name, objAction, start_frame, end_frame, layer, playByParent, activated, soundFileName)   
        self.pause_colourAction = pause_colourAction
        self.play_colourAction = play_colourAction
        self.play_mode = MENU_MODE_PLAY_STOP
        self.pause_mode = False
        self.count = False
        self.highlight_play(False)
        self.highlight_pause(False)        

    @property
    def activated(self):
        return self._activated
    
    @activated.setter
    def activated(self, value):
        tracking_n = random.random()
         
      
        # (code 1) when previous status is not activated, value = True means it should be activate.  Nothing to do with pause mode  
        # (code 2) when previous status is activated, then value = True would not change its value but would change its pause mode,
        # (code 3) when previous status is not activated, then value = False would not change its value, Nothing to do with pause mode
        # (code 4) when previous status is activated, then when value = False (e.g. trigger by external) would change its value to off.
        
        self.count = not self.count   # swap count so that the setter only work in interval
        if G.skip_count or self.count:
            print('-',tracking_n , '** running activated.setter **** self and value and track no ***', \
                    self, ',', value )
            if value:  # key pressed
                if not self._activated:  # code 1 when previous status is not activated    

                    print('running code 1:  play activated from off to on -', tracking_n, \
                    ' self._activated ', self._activated)
                    
                    self._activated = True
                    self.play_mode = MENU_MODE_PLAY_START
                    self.playAction()
                    self.highlight_play(True)
                    print('now:  self._activated: ', self._activated)

                else:    # code 2 when previous status is activated
                    print('running code 2: play activated from on to on -',tracking_n , \
                    '-self and value --',  self, ',', value, \
                    '\npause mode before change is :', self.pause_mode)
                    
                    self.pause_mode = not self.pause_mode # switch pause mode
                    print('now change pausemode to: ', self.pause_mode)

                    if self.pause_mode:  
                        self.play_mode = MENU_MODE_PLAY_PAUSE
                        self.highlight_pause(True)  # if it is a pause, turn on pause

                    else:  # if the switch is from pause to play again
                        self.play_mode = MENU_MODE_PLAY_RESUME
                        self.highlight_pause(False)  # if it is not a pause
                        

         

    def deactivated(self):
        #if self._activated:
        if self.activated:  self.highlight_play(False)
        if self.pause_mode:  self.highlight_pause(False)
        self.play_mode = MENU_MODE_PLAY_STOP
    

        print('deactivate the play button')

        self._activated = False
        self.pause_mode = False

    
    
    

    def highlight_play(self, mode):
        # to change colour of the button according to action
        if mode:
            print('press button is pressed when previous state is not activated:  code 1')
            print('play_colourAction', self.play_colourAction, ' at layer', self.layer+8)
            self.speakerObj.playAction(self.play_colourAction, self.start_frame, self.end_frame, priority=0, layer=self.layer+8)
        else: 
            self.speakerObj.playAction(self.play_colourAction, self.end_frame, self.start_frame, priority=0, layer=self.layer+8)
        
        
    def highlight_pause(self, mode):
        # to change colour of the button according to action
        if mode:
            print('highlight_pause(True, playing ', self.pause_colourAction)
            self.speakerObj.playAction(self.pause_colourAction, self.start_frame, self.end_frame, priority=0, layer=self.layer)
        else:
            self.speakerObj.playAction(self.pause_colourAction, self.end_frame, self.start_frame,  priority=0, layer=self.layer)
        
    
# a super class which generate sub class according to different types of sensor media (i.e. mouse or key)
class ArrowMenu:
 
    def __init__(self, mediaDict):
        self.debug = False
        self.mediaDict = mediaDict
        if self.debug:
            print("mediaDict: ", mediaDict)
        
        self.arrowPlay = mediaDict['arrowPlay']['menu_object']
        self.arrowStop = mediaDict['arrowStop']['menu_object']
        self.arrowForward = mediaDict['arrowForward']['menu_object']
        self.arrowBack = mediaDict['arrowBack']['menu_object']
        
        #self.play_mode = MENU_MODE_STOP
        #self.pause_mode = false
            
    def sensor_query_(self, key_value):
        # this method would be overrided by individual subclass based on its own sensor 
        # mechanism
        query_result = False
        return query_result
        
  
    def addDict(self, name, mediaDict):
        self.mediaDict[name]=mediaDict

    def update(self, call_back_play = None, call_back_pause = None, \
        call_back_resume = None, call_back_stop = None, call_back_backward=None, call_back_forward=None):
        # run every frame
        # check the mouseOver sensor for each of the menu obj in the mouseDict 
        ccnt = G.getCurrentController()
        for key in self.mediaDict:
            key_value = self.mediaDict[key]
            menu_object = self.mediaDict[key]['menu_object']  
            # remember menu_object is not a game object but an instancce of class ArrowMenu
            
            if self.sensor_query(key_value):
                #menu_object.status = G.KX_INPUT_JUST_ACTIVATED
                menu_object.activated=True    # the outcome that some key is pressed in stored in global parameter

    #           coordinate between different menu arrow:  e.g. a stop will deactivate the play    
                #if self.arrowStop.activated:
                if key == 'arrowStop':
                    self.arrowPlay.deactivated() 
                    if self.arrowPlay.play_mode == MENU_MODE_PLAY_STOP and call_back_stop:
                            print('running stop to play', call_back_stop)
                            call_back_stop()
                    
                if key == 'arrowBack':
                    self.arrowPlay.deactivated() 
                    print('running backward call back', call_back_backward)
                    if call_back_backward:  call_back_backward()
                if key == 'arrowForward':
                    self.arrowPlay.deactivated() 
                    print('running forward call back', call_back_forward)
                    if call_back_forward:  call_back_forward()
                
                            
                            
                if key == 'arrowPlay':
                    if menu_object.play_mode == MENU_MODE_PLAY_START and call_back_play:
                        print('running start to play', call_back_play)
                        call_back_play()
                        
                    if menu_object.play_mode == MENU_MODE_PLAY_PAUSE and call_back_pause:
                    
                        print('trigger pause mode', call_back_pause)
                        call_back_pause()
                    if menu_object.play_mode == MENU_MODE_PLAY_RESUME and call_back_resume:
                        
                        print('trigger pause mode', call_back_resume)
                        call_back_resume()


                        
                        
                    
                    


        
class ArrowMenuMouse(ArrowMenu):
 # a subclass of ArrowMenu for menu item object.  the method update is overrided 
 # by individual feature of media feature, either mouse, key or touch screen
 
 # add mouse 02/09/2022
# but perhaps easier to use logic brick for mouse, as it needs certain transformation (ray casting)
# to detect mouse over and programming may be a bit complicated

    def __init__(self, mediaDict):
        super().__init__(mediaDict)
        
    
    def sensor_query(self, key_value):
        query_result = None
        #if G.defaultMouseLeftSensor is not None:  # there is option of using logic brick or python for the object
        if 's_mouseOver' in key_value:  # there is option of using logic brick or python for the object
            # use logic brick by their sensor name in the key_value
            query_result = self.sensor_query_bricks(key_value)
            
        else:  # if there is no name for the key_value input, thenn use python 
            query_result = self.sensor_query_python(key_value)
            
        return query_result
    
    def sensor_query_bricks(self, key_value):   
        
        if mouseLeft():
            
            cont = G.getCurrentController()
            #sen_mouseLeft=cont.sensors[key_value['s_mouseLeft']]
            sen_mouseOver=cont.sensors[key_value['s_mouseOver']]

            

            print('self and sen_mouseOver:', self, ': ', sen_mouseOver, dir(sen_mouseOver), '\n')

            
        return (mouseLeft() and sen_mouseOver.positive)
        


    def sensor_query_python(self, key_value):   
            
        scene = G.getCurrentScene()
        
        if 'menu_camera' in key_value:
            cam = scene.objects[key_value['menu_camera']]
        else:
            cam = G.default_menu_camera
            
        obj = key_value['menu_object'].get_game_obj()
        
        return (mouseLeft() and mouseOver(obj, cam))
    
def mouseLeft():
    
    return G.KX_INPUT_JUST_ACTIVATED in G.mouse.inputs[bge.events.LEFTMOUSE].queue
    
        
def mouseOver(obj, cam):

    cam_location = cam.worldPosition
    x, y = G.mouse.position
    mouse_to_cam_vector = cam.getScreenVect(x, y)
    mouse_location = cam_location - mouse_to_cam_vector
    max_dist_to_look = 50
    hit = cam.rayCast(mouse_location,cam_location,max_dist_to_look)[0]
    
    #print('rupnning mouseOver on obj:', obj.name, 'with cam: ', cam.name, ' hit:', hit.name, '.  query_result:', query_result)
    #if hit.name == obj.name:
    #    print('obj:', obj, '.  hit: ', hit)
    
    #print('cam_location:', cam_location,'.  mouse_to_cam_vector', mouse_to_cam_vector, ', mouse_location:', mouse_location, 'hit:', hit, 'mouse location at screen x, y:', x, ', ', y)
    
    return True if hit == obj else None

    
class ArrowMenuKey(ArrowMenu):
# because it replace the logic block of keyboard it will need to add a logic block of always
# enabling Pulse mode to trigger the controller


 # a subclass of ArrowMenu for menu item object.  the method update is overrided 
 # by individual feature of media feature, either mouse, key or touch screen
    def __init__(self, mediaDict):
        super().__init__(mediaDict)

    def sensor_query(self, key_value):     
        return G.KX_INPUT_JUST_ACTIVATED in G.keyboard.inputs[key_value['assignKey']].queue   




          


######################################### init starts here ###########################################################



def initMenu(cont):
# configure the arrow object, its action
# it will be called by a logic brick sensor always without pulse mode on, and linked to a controller which is
# marked with priority - hence it is called just once, and at the start of the game prior to any other 
# controller

    scene = G.getCurrentScene()
    camList = scene.cameras
    G.skip_count = False
    # note that start and end frame for all action should be standardardized to 1 and 5. 
    G.arrowPlay = Menu_button_play(objAction = 'arrowAction', layer =4, name = 'arrowPlay',\
        activated=False, start_frame= 1, end_frame =5, \
        play_colourAction='arrowPlay_play_mode_Action', \
        pause_colourAction='arrowPlay_pause_mode_Action')  
    G.arrowStop = Menu_button(objAction = 'arrowAction', layer =4, name = 'arrowStop', activated=False, \
    start_frame= 1, end_frame =5)  
    G.arrowBack = Menu_button(objAction = 'arrowAction', layer =4, name = 'arrowBack', activated=False, \
    start_frame= 1, end_frame =5) 
    G.arrowForward = Menu_button(objAction = 'arrowAction', layer =4, name = 'arrowForward', activated=False, \
    start_frame= 1, end_frame =5)  
    
    print('arrowPlay is: ', G.arrowPlay, 'name: ', G.arrowPlay.name)
    
    # configure the mouse dictionary w.r.t its logic bricks
    # the mouseDict contains also a list of menu items with attribute about each mouse sensor which would trigger the menu item.
    # an object arrow_menu_mouse is created in which there is a method update() to check each sensor and instruct the object for each 
    # menu item to response (item object's action) and register (item menu object's attribute 'activated')
    #
    #G.defaultMouseLeftSensor = 's_menuScript_mouseLeft'
    #G.defaultMouseLeftSensor = None
    #menu_camera = 'cup_of_tea_camera'  # the camera intend to calculate mouse position, for using alan and nina it might be another camera
    menu_camera = 'menu_camera'  
    if menu_camera in camList:
        G.default_menu_camera = camList[menu_camera]# the camera intend to calculate mouse position, for using alan and nina it might be another camera
    else:
        G.default_menu_camera = scene.active_camera    # the camera intend to calculate mouse position, for using alan and nina it might be another camera
    print('menu camera is:', G.default_menu_camera)
    G.mouseDict = {}
    G.mouseDict['arrowPlay'] = { 'menu_object' : G.arrowPlay}
    G.mouseDict['arrowStop'] = { 'menu_object': G.arrowStop}
    G.mouseDict['arrowBack'] = { 'menu_object': G.arrowBack}    
    G.mouseDict['arrowForward'] = {'menu_object': G.arrowForward}

    # configure the key dictionary w.r.t its key assigned constant
    G.keyDict = {}
    G.keyDict['arrowPlay'] = {'assignKey': bge.events.AKEY, 'menu_object' : G.arrowPlay}
    G.keyDict['arrowStop'] = {'assignKey': bge.events.SKEY, 'menu_object' : G.arrowStop}
    G.keyDict['arrowBack'] = {'assignKey': bge.events.DKEY, 'menu_object' : G.arrowBack}    
    G.keyDict['arrowForward'] = {'assignKey': bge.events.FKEY, 'menu_object' : G.arrowForward}
    
            
    G.flag_mouse = True
    G.flag_key = True
    G.play_action_flag = True
    if G.flag_mouse == True: bge.render.showMouse(True)
    
    # for info only, not used in coding, fileInfo store the blender file which I am working on or testing with
    fileInfo = {0:'cdMenuV1.blend',1:'playingAssetsTwoCubesV1a.blend', 2:'playingAssetAppendReuseV4.blend'}  


    # create objects: one for mouse menu and one for keyboard 
    G.arrow_menu_key = ArrowMenuKey(G.keyDict)
    G.arrow_menu_mouse = ArrowMenuMouse(G.mouseDict)
    
    
    
def run_arrowMenu_backup(cont):   
    
# to test the use of class SceneMenu which poll user's choice of arrow menu on
# screen using keyboard
# 02/09/2022  work with menuTesting.blend

    # logic bricks with mouse available for menu selection

    if G.flag_mouse:  G.arrow_menu_mouse.update()
        
    if G.flag_key: G.arrow_menu_key.update()

        
  