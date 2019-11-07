import mset
from vmd import VMD

def import_fov():
    
    vmd_path = mset.showOpenFileDialog(['vmd'])
    if vmd_path == '':
        mset.shutdownPlugin()
    vmd = VMD()
    vmd.read_file(vmd_path)
    
    mmd_camera_parent = mset.getSelectedObject()
    if not isinstance(mmd_camera_parent, mset.CameraObject):
        mset.shutdownPlugin()
    mmd_camera = mset.CameraObject(name='MMD Camera')
    mmd_camera.parent = mmd_camera_parent

    timeline = mset.getTimeline()
    frame_list = []
    for i in range(len(vmd.camera_keyframe_record)):
        cam_rec = vmd.camera_keyframe_record[i]
        frame_list.append(cam_rec['FrameTime'])
    
    timeline.totalFrames = max(timeline.totalFrames, max(frame_list) + 30)



    for i in range(len(vmd.camera_keyframe_record)):
        cam_rec = vmd.camera_keyframe_record[i]
        timeline.currentFrame = cam_rec['FrameTime']
        mmd_camera.fov = float(cam_rec["ViewAngle"])
        mmd_camera.setKeyframe('linear')
        

    
    timeline.currentFrame = 0
    mset.shutdownPlugin()

def close_callback():
    mset.shutdownPlugin()


if __name__ == '__main__':
    #create a window
    mmd_window = mset.UIWindow("MMD CAM FOV")
    fov_label = mset.UILabel('Select mmd camera from abc file.')
    fov_button = mset.UIButton("Import FOV")
    fov_button.onClick = import_fov
    
    close_button = mset.UIButton("Close")
    close_button.onClick = close_callback

    #add the button to the window
    mmd_window.addElement(fov_label)
    mmd_window.addReturn()
    mmd_window.addElement(fov_button)
    mmd_window.addElement(close_button)


    
