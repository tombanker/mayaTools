import maya.cmds as cmds
import maya.mel as mel
import utils as utils

class RibbonLimb(object):

    def __init__(self, name, numJnts, width, lengthRatio, setupCons):
        super(RibbonLimb, self).__init__()
        self.name = name
        self.numJnts = numJnts
        self.width = width
        self.lengthRatio = lengthRatio
        self.setupCons = setupCons

        self.buildRibbonLimb()

    def buildRibbonLimb(self):
        # Organize hiearchy nodes and groups
        self.rootGrp = cmds.group(em=1, n='%s01' % self.name)
        self.moveGrp = cmds.group(em=1, n='%s_globalMove01' % self.name)
        self.extrasGrp = cmds.group(em=1, n='%s_extraNodes01' % self.name)
        cmds.parent(self.extrasGrp, self.rootGrp)

        myRibbonPlane = self.buildRibbonPlane()
        myControls = self.buildControls(self.setupCons)
        self.buildDeformers(myRibbonPlane[0], myControls, myRibbonPlane[1])

    def buildRibbonPlane(self):
        # Create Nurbs surface
        flexiPlane = cmds.nurbsPlane(w=self.width, lr=self.lengthRatio,
                                     u=self.numJnts, v=1, ax=[0, 1, 0])
        flexiPlane = cmds.rename(flexiPlane[0], '%s_surface01' % self.name)
        cmds.delete(flexiPlane, constructionHistory=1)

        # Create plane follicles
        mel.eval('createHair %s 1 2 0 0 0 0 1 0 1 1 1;' % str(self.numJnts))
        for obj in ['hairSystem1', 'pfxHair1', 'nucleus1']:
            cmds.delete(obj)
        folChildren = cmds.listRelatives('hairSystem1Follicles', ad=1)
        cmds.delete([i for i in folChildren if 'curve' in i])
        folGrp = cmds.rename('hairSystem1Follicles', '%s_flcs01' % self.name)

        alphabetList = map(chr, range(97, 123))
        folChildren = cmds.listRelatives(str(folGrp), c=1)
        folJnts = []

        for obj, letter in zip(folChildren, alphabetList):
            folJnt = cmds.joint(p=cmds.xform(obj, t=1, q=1), n='%s_bind_%s01' % (self.name, letter))
            folJnts.append(folJnt)
            cmds.parent(folJnt, obj)
            cmds.rename(obj, '%s_flc_%s01' % (self.name, letter))

        utils.lockAttrs(flexiPlane, 1, 1, 1, 0)

        cmds.parent(folGrp, self.extrasGrp)
        cmds.parent(flexiPlane, self.moveGrp)

        return flexiPlane, folGrp

    def buildControls(self, createControls=True):
        # Create a global move control
        globalCon = self.utils.createStarControl(name='%s_con_global01' % self.name, radius=1.5)
        cmds.setAttr('%s.overrideEnabled' % globalCon, 1)
        cmds.setAttr('%s.overrideColor' % globalCon, 17)

        cmds.addAttr(globalCon, at='enum', ln='maintainVolume', en='---', k=1)
        cmds.setAttr('%s.maintainVolume' % globalCon, k=0, l=1, cb=1)
        cmds.addAttr(globalCon, at='bool', ln='volEnable', k=1)

        cmds.parent(globalCon, self.rootGrp)
        cmds.parent(self.moveGrp, globalCon)

        # Create FK controls if option selected
        if createControls:

            transCons = ['%s_con_a01' % self.name, '%s_con_b01' % self.name, '%s_midBend01' % self.name]

            for squareCon in transCons:
                squareCon = cmds.curve(n=squareCon, d=1, p=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)])
                cmds.scale(.75, .75, .75, squareCon, r=1)
                cmds.setAttr('%s.overrideEnabled' % squareCon, 1)
                cmds.setAttr('%s.overrideColor' % squareCon, 17)
                cmds.xform(squareCon, roo='xzy')
                squareShape = cmds.listRelatives(squareCon, type='shape')
                cmds.rename(squareShape, '%sShape' % squareCon)

            topCon = transCons[0]
            botCon = transCons[1]
            midCon = transCons[2]

            cmds.xform(topCon, t=(-self.width / 2, 0, 0), ws=1)
            cmds.xform(botCon, t=(self.width / 2, 0, 0), ws=1)
            cmds.xform(midCon, t=(0, 0, 0), ws=1)
            cmds.makeIdentity(transCons, a=1)

            squareConGrp = cmds.group(topCon, botCon, n='%s_cons01' % self.name)
            midConGrp = cmds.group(midCon, n='%s_midCon01' % self.name)
            cmds.parent(midConGrp, squareConGrp)
            cmds.pointConstraint(botCon, topCon, midConGrp, mo=0)

            # Lock and hide controller attrs
            utils.lockAttrs(topCon, 0, 0, 1, 1)
            utils.lockAttrs(botCon, 0, 0, 1, 1)
            utils.lockAttrs(midCon, 0, 1, 1, 1)

            for con in transCons:
                cmds.setAttr('%s.rotateY' % con, l=1, k=0, cb=0)
                cmds.setAttr('%s.rotateZ' % con, l=1, k=0, cb=0)

            cmds.parent(squareConGrp, self.moveGrp)

            return transCons, globalCon

        else:
            return [globalCon]

    def buildDeformers(self, ribbonPlane, controls=(), folGrp=()):
        # Create a target blendshape controlled by deformers
        flexiBlend = cmds.duplicate(ribbonPlane, n='flexiPlaneSetup_bShp_surface01')
        flexiBlendNode = cmds.blendShape(flexiBlend, ribbonPlane, n='%s_bShpNode_surface01' % self.name)

        # Turn blendshape on
        cmds.setAttr('%s.%s' % (flexiBlendNode[0], flexiBlend[0]), 1)

        # Create a wire deformer controled by ribbon controls
        wireCurve = cmds.curve(
            n='%s_wire_surface01' % self.name, d=2, p=[(-self.numJnts, 0, 0), (0, 0, 0), (self.numJnts, 0, 0)])
        topClstr = cmds.cluster('%s.cv[0:1]' % wireCurve, rel=1, n='%s_cl_a01' % self.name)
        midClstr = cmds.cluster('%s.cv[1]' % wireCurve, rel=1, n='%s_cl_mid01' % self.name)
        botClstr = cmds.cluster('%s.cv[1:2]' % wireCurve, rel=1, n='%s_cl_b01' % self.name)
        clsGrp = cmds.group(topClstr, midClstr, botClstr, n='%s_cls01' % self.name)

        for attr in ['scalePivot', 'rotatePivot']:
            cmds.setAttr('%s.%s' % (topClstr[1], attr), -self.numJnts, 0, 0)
        for attr in ['scalePivot', 'rotatePivot']:
            cmds.setAttr('%s.%s' % (botClstr[1], attr), self.numJnts, 0, 0)

        cmds.setAttr('%sShape.originX' % topClstr[1], (-self.numJnts))
        cmds.setAttr('%sShape.originX' % botClstr[1], (self.numJnts))
        cmds.percent(topClstr[0], '%s.cv[1]' % wireCurve, v=0.5)
        cmds.percent(botClstr[0], '%s.cv[1]' % wireCurve, v=0.5)

        # Create twist and wire blend shape deformers
        twistNode = cmds.nonLinear(flexiBlend, type='twist')
        cmds.wire(flexiBlend, w=wireCurve, dds=[0, 20], foc=0, n='%s_wireAttrs_surface01' % self.name)
        cmds.xform(twistNode, ro=(0, 0, 90))
        twistNode[0] = cmds.rename(twistNode[0], '%s_twistAttrs_surface01' % self.name)
        twistNode[1] = cmds.rename(twistNode[1], '%s_twist_surface01' % self.name)

        # Setup squash and stretch via utilitiy nodes
        arcLen = cmds.arclen(wireCurve, ch=1)
        arcLen = cmds.rename(arcLen, '%s_curveInfo01' % self.name)
        arcLenValue = cmds.getAttr('%s.arcLength' % arcLen)
        squashDivNode = cmds.createNode('multiplyDivide', n='%s_div_squashStretch_length01' % self.name)
        volDivNode = cmds.createNode('multiplyDivide', n='%s_div_volume01' % self.name)
        squashCondNode = cmds.createNode('condition', n='%s_cond_volume01' % self.name)

        cmds.setAttr('%s.operation' % squashDivNode, 2)
        cmds.setAttr('%s.input2X' % squashDivNode, arcLenValue)
        cmds.setAttr('%s.operation' % volDivNode, 2)
        cmds.setAttr('%s.input1X' % volDivNode, 1)
        cmds.setAttr('%s.secondTerm' % squashCondNode, 1)

        cmds.connectAttr('%s.arcLength' % arcLen, '%s.input1X' % squashDivNode)
        cmds.connectAttr('%s.outputX' % squashDivNode, '%s.input2X' % volDivNode)
        cmds.connectAttr('%s.outputX' % volDivNode, '%s.colorIfTrueR' % squashCondNode)

        # Set visibility options
        for obj in [flexiBlend[0], wireCurve, twistNode[1], clsGrp]:
            cmds.setAttr('%s.visibility' % obj, 0)

        # Connect controls to cluster deformers if they exist
        if len(controls) > 1:
            topCon = controls[0][0]
            botCon = controls[0][1]
            midCon = controls[0][2]

            for con, clstr in zip([topCon, botCon], [topClstr[1], botClstr[1]]):
                cmds.connectAttr('%s.translate' % con, '%s.translate' % clstr)

            cmds.connectAttr('%s.translate' % midCon, '%s.translate' % midClstr[1])

            # Connect controls to twist deformer
            cmds.connectAttr('%s.rotateX' % topCon, '%s.endAngle' % twistNode[0])
            cmds.connectAttr('%s.rotateX' % botCon, '%s.startAngle' % twistNode[0])
            cmds.connectAttr('%s.volEnable' % controls[1], '%s.firstTerm' % squashCondNode)

        # Scale contraint each follicle to global move group
        for fol in cmds.listRelatives(folGrp, c=1):
            cmds.scaleConstraint(self.moveGrp, fol, mo=0)
            for shape in cmds.listRelatives(fol, s=1):
                cmds.setAttr('%s.visibility' % shape, 0)

        # Parent nodes
        cmds.parent(flexiBlend, wireCurve, clsGrp, twistNode[1],
                    '%s_wire_surface01BaseWire' % self.name, self.extrasGrp)
