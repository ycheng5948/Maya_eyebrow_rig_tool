from maya import cmds
import maya.mel as mm

class eyebrow_rig(object):

    #constructor
    def __init__(self):

        self.window = 'eyebrow_rig'
        self.title = 'Eyebrow Rig'
        self.size = (600, 600)

        # close old window if open
        if cmds.window(self.window, exists = True):
            cmds.deleteUI(self.window, window=True)

        #create new window
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)

################################################################### UI CONTENT

        cmds.columnLayout(adjustableColumn = True)

        cmds.separator(h=10)
        cmds.text(self.title, h=30)
        cmds.separator(height=10)

###################################################################
        #CHECK JOINTS' NAMES
        cmds.separator(h=10)

        cmds.text(label='Rename joint to \"eyebrows_index\"')
        cmds.text(label='')

        self.rename_brow = cmds.button(label='Rename', command=self.rename_brow)
        self.rename_TarJNT = cmds.ls(sl=True)

###################################################################
        #CREATE
        cmds.separator(h=10)

        cmds.text(label='III. Create!')
        cmds.text(label='')
        self.CreateRig = cmds.button(label='Create', command=self.CreateRig)
        cmds.text(label='')

###################################################################

        #display new window
        cmds.showWindow()

################################################################### ACTION

    def rename_brow(self, *arg):
        self.rename_TarJNT = cmds.ls(sl=True)
        cmds.select(self.rename_TarJNT, hi=True)
        rename_joints = cmds.ls(sl=True, type='joint')
        print(rename_joints)

        for index, jnt in enumerate(rename_joints):
            print(jnt)
            cmds.rename(jnt, 'eyebrow_{0}_JNT'.format(index))

###################################################################

    def CreateRig(self, *args):

        self.First_TarJNT = cmds.ls(sl=True)
        cmds.select(self.First_TarJNT, hi=True)

        self.TarJNTs = cmds.ls(sl=True)
        jnt_num = len(self.TarJNTs)

        # creating joints
        tra_jnt = cmds.duplicate(self.TarJNTs[0], name='tra', rc=1)
        for index, jnt in enumerate(tra_jnt):
            cmds.rename(jnt, 'eyebrow_tra_{0}_JNT'.format(index))

        rot_jnt = cmds.duplicate(self.TarJNTs[0], name='rot', rc=1)
        for index, jnt in enumerate(rot_jnt):
            cmds.rename(jnt, 'eyebrow_rot_{0}_JNT'.format(index))
            cmds.parent('eyebrow_rot_{0}_JNT'.format(index), 'eyebrow_tra_{0}_JNT'.format(index))

        ik_jnt = cmds.duplicate(self.TarJNTs[0], name='ik', rc=1)
        for index, jnt in enumerate(ik_jnt):
            cmds.rename(jnt, 'eyebrow_ik_{0}_JNT'.format(index))

        #creating spline ik handle
        mm.eval('''
                select -r eyebrow_ik_0_JNT ;
                select -add eyebrow_ik_{0}_JNT ;
                ikHandle -sol ikSplineSolver -ns {0};
                '''.format(jnt_num-1))
        
        cmds.rename('effector1', 'eyebrow_effector')
        cmds.rename('curve1', 'eyebrow_CRV')
        cmds.rename('ikHandle1','eyeborw_HND')
        cmds.setAttr('eyeborw_HND.dTwistControlEnable', 1)
        cmds.setAttr('eyeborw_HND.dWorldUpType', 4)

        spl_jnt = cmds.duplicate(self.TarJNTs[0], name='spl', rc=1)
        cmds.rename('spl', 'eyebrow_spl_0_JNT')
        new_spl_jnt = []
        new_spl_jnt.append('eyebrow_spl_0_JNT')
        a = jnt_num-1
        for jnt in spl_jnt[:0:-1]:
            cmds.rename(jnt, 'eyebrow_spl_{0}_JNT'.format(a))
            cmds.parent('eyebrow_spl_{0}_JNT'.format(a), w=1)
            new_spl_jnt.insert(1, 'eyebrow_spl_{0}_JNT'.format(a))
            a-=1
        
        # if there are more than 5 joints
        if jnt_num-1 >= 5:
            for jnt in new_spl_jnt[1::2]:
                cmds.delete(jnt)
                new_spl_jnt.remove(jnt)
            for index, jnt in enumerate(new_spl_jnt):
                cmds.rename(jnt, 'eyebrow_spl_{0}_JNT'.format(index))

        cmds.delete(self.TarJNTs)

        print('Joints Created!!')

        #creating ball ctrl
        cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='A')
        cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), n='B')
        cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), n='C')
        crvGrp = cmds.group(em=True, name='ball_CRV')
        crvShape = ['AShape', 'BShape', 'CShape']
        cmds.parent(crvShape,crvGrp,s=1,r=1)
        cmds.delete('A', 'B', 'C')
        crvGrp = cmds.group(em=True, name='ball_GRP')
        cmds.parent('ball_CRV', 'ball_GRP')

        # moving and parenting the ball ctrls
        ctrl_jnt = []
        for i in range(5):
            ctrl_jnt.append('eyebrow_spl_{0}_JNT'.format(i))

        cmds.select(ctrl_jnt)
        joints = cmds.ls (sl=True)

        cmds.group(em=True, name='eyebrow_spl_GRP')
        cmds.parent(joints, 'eyebrow_spl_GRP')
        for jnt in joints:
            grp = cmds.duplicate('ball_GRP', name='eyebrow_{0}_CTRL_GRP'.format(jnt.split('_')[2]), rc=1)[0]
            ctrl = cmds.listRelatives(grp, c=True)[0]
            ctrl = cmds.rename(ctrl, 'eyebrow_{0}_CTRL'.format(jnt.split('_')[2]))
            cmds.delete(cmds.parentConstraint(jnt, grp, mo=False))
            cmds.parentConstraint(ctrl, jnt, mo=1)

        cmds.delete('ball_GRP')

        # setting up ctrls' constraints
        cmds.parentConstraint('eyebrow_0_CTRL', 'eyebrow_2_CTRL', 'eyebrow_1_CTRL_GRP', mo=1)
        cmds.parentConstraint('eyebrow_2_CTRL', 'eyebrow_4_CTRL', 'eyebrow_3_CTRL_GRP', mo=1)

        # setting eyeborw_HND world up objects' attributes
        cmds.connectAttr('eyebrow_0_CTRL.worldMatrix[0]', 'eyeborw_HND.dWorldUpMatrix')
        cmds.connectAttr('eyebrow_4_CTRL.worldMatrix[0]', 'eyeborw_HND.dWorldUpMatrixEnd')

        # skinning spl_jnts to crv
        cmds.skinCluster(joints, 'eyebrow_CRV', dr=4)

        # setting up ik_jnt to tra_jnt and rot_jnt contraints
        ik_jnt = cmds.ls('eyebrow_ik_*_JNT')
        tra_jnt = cmds.ls('eyebrow_tra_*_JNT')
        rot_jnt = cmds.ls('eyebrow_rot_*_JNT')
        for i in range(jnt_num):
            cmds.orientConstraint(ik_jnt[i], rot_jnt[i], mo=1)
            cmds.pointConstraint(ik_jnt[i], tra_jnt[i], mo=1)

        # setting up strech
        crv = 'eyebrow_CRV'

        # setting up Locator
        cmds.spaceLocator(n='eyebrow_settings_LOC')
        settings_shape = 'eyebrow_settings_LOCShape'
        cmds.addAttr(settings_shape, at='double', ln='stretch', min=0, max=1, dv=0, k=True)

        # parenting LOC to ctrls and hide
        ctrls = cmds.ls('eyebrow_*_CTRL')
        for x in ctrls:
            cmds.parent(settings_shape, x, r=True, s=True, add=True)

        cmds.hide('eyebrow_settings_LOCShape')

        # create ALD and set the uParamValue to eyebrow_CRVShape max value
        ald = cmds.createNode('arcLengthDimension', n='eyebrow_ALDShape')
        cmds.connectAttr('{0}.worldSpace[0]'.format(crv), '{0}.nurbsGeometry'.format(ald))

        max_value = cmds.getAttr('eyebrow_CRVShape.mmv.max')
        cmds.setAttr('{0}.uParamValue'.format(ald), max_value)

        # create MDN and set to devide(2)
        eyebrow_stretch_devide_MDN = cmds.createNode('multiplyDivide', n='eyebrow_stretch_MDN')
        cmds.setAttr('{0}.operation'.format(eyebrow_stretch_devide_MDN), 2)
        cmds.connectAttr('{0}.arcLength'.format(ald), '{0}.input1X'.format(eyebrow_stretch_devide_MDN))
        imput2X_value = cmds.getAttr('{0}.input1X'.format(eyebrow_stretch_devide_MDN))
        cmds.setAttr('{0}.input2X'.format(eyebrow_stretch_devide_MDN), imput2X_value)

        ik_jnt = cmds.ls('eyebrow_ik_*_JNT')
        # setting up MDN and BLC for all ik_jnts
        for jnt in ik_jnt:
            # create MDN, set to multiply(1) and connect
            eyebrow_ik_stretch_MDN = cmds.createNode('multiplyDivide', n='{0}_stretch_MDN'.format(jnt.replace('_JNT', '')))
            cmds.setAttr('{0}.operation'.format(eyebrow_ik_stretch_MDN), 1)
            cmds.connectAttr('{0}.outputX'.format(eyebrow_stretch_devide_MDN), '{0}.input1X'.format(eyebrow_ik_stretch_MDN))

            JNT_translate_x = cmds.getAttr('{0}.tx'.format(jnt))
            cmds.setAttr('{0}.input2X'.format(eyebrow_ik_stretch_MDN), JNT_translate_x)
            
            # create BLC and connect
            eyebrow_stretch_BLC = cmds.createNode('blendColors', n='{0}_stretch_BLC'.format(jnt.replace('_JNT', '')))
            cmds.connectAttr('{0}.outputX'.format(eyebrow_ik_stretch_MDN), '{0}.color1R'.format(eyebrow_stretch_BLC))
            cmds.setAttr('{0}.color2R'.format(eyebrow_stretch_BLC), JNT_translate_x)
            cmds.connectAttr('{0}.outputR'.format(eyebrow_stretch_BLC), '{0}.tx'.format(jnt))

            cmds.connectAttr('{0}.stretch'.format(settings_shape), '{0}.blender'.format(eyebrow_stretch_BLC))
        
        # hide locked and unused attributes of the locator shape
        cmds.setAttr('eyebrow_settings_LOCShape.lpx', channelBox=0, keyable=0)
        cmds.setAttr('eyebrow_settings_LOCShape.lpy', channelBox=0, keyable=0)
        cmds.setAttr('eyebrow_settings_LOCShape.lpz', channelBox=0, keyable=0)
        cmds.setAttr('eyebrow_settings_LOCShape.lsx', channelBox=0, keyable=0)
        cmds.setAttr('eyebrow_settings_LOCShape.lsy', channelBox=0, keyable=0)
        cmds.setAttr('eyebrow_settings_LOCShape.lsz', channelBox=0, keyable=0)



#IN Maya
#eyebrow_rig_tool.eyebrow_rig()
