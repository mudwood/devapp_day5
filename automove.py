from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, Vehicle
from pymavlink import mavutil
import time
import math
import threading

###############################################################################
#   description :   globalframeの座標同士の距離を求める(m)
#                   高度は考慮されていない
#   function    :   get_distance_meters
#   parameters  :   loc1, loc2
###############################################################################
def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

###############################################################################
#   description :   自動航行
#   function    :   AutoMove
#   parameters  :   connection,     接続文字列
#                   fileName,       実行するファイル（mpから出力されたもの
#                   isCopter,       コプターか？
#                   isBlock         実行完了を待つ（最後のwpに到達で完了とした）
###############################################################################
def AutoMove( connection, fileName, isCopter, isBlock ):

    vheicle = connect( connection, wait_ready=True, timeout=60 )      # rover taigan
    print("Connected.", connection, fileName)

    vheicle.parameters[ 'WP_RADIUS' ] = 2   # wpマージン(m)
    print("set wp_radius=2")

    # ##### ミッションの内容（一度DLして cmds を初期化しないとうまくいかない？）
    cmds = vheicle.commands
    cmds.download()
    cmds.wait_ready()

    ( commands, lats, lons, alts ) = mpReader( fileName )

    for command, lat, lon, alt in zip( commands, lats, lons, alts ):
        print( command, lat, lon, alt )

    cmds = vheicle.commands
    cmds.clear()                                            # 現在のミッションをクリア
    cmds.upload()
    cmds.wait_ready()

    latestLat = -1
    latestLon = -1
    for command, lat, lon, alt in zip( commands, lats, lons, alts ):
        if command == 22:       # MAV_CMD_NAV_TAKEOFF
            cmd = Command(  0,                                           # system id
                            0,                                           # component id
                            1,                                           # seq
                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,   #frame
                            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,    # MAV_CMD
                            0,   # current
                            1,   # auto continue
                            0,   # param 1
                            0,   # param 2
                            0,   # param 3
                            0,   # param 4
                            lat,   # param 5
                            lon,   # param 6
                            alt )  # param 7
            cmds.add( cmd )                                     # コマンドの追加
            cmds.upload()
            
        elif command == 16:     # MAV_CMD_NAV_WAYPOINT
            cmd = Command(  0,                                           # system id
                            0,                                           # component id
                            1,                                           # seq
                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,   #frame
                            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,    # MAV_CMD
                            0,   # current
                            1,   # auto continue
                            0,   # param 1
                            0,   # param 2
                            0,   # param 3
                            0,   # param 4
                            lat,   # param 5
                            lon,   # param 6
                            alt )  # param 7
            cmds.add( cmd )                                     # コマンドの追加
            cmds.upload()

            latestLat = lat
            latestLon = lon

        elif command == 21:     # MAV_CMD_NAV_LAND
            cmd = Command(  0,                                           # system id
                            0,                                           # component id
                            1,                                           # seq
                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,   #frame
                            mavutil.mavlink.MAV_CMD_NAV_LAND,    # MAV_CMD
                            0,   # current
                            1,   # auto continue
                            0,   # param 1
                            0,   # param 2
                            0,   # param 3
                            0,   # param 4
                            lat,   # param 5
                            lon,   # param 6
                            alt )  # param 7
            cmds.add( cmd )                                     # コマンドの追加
            cmds.upload()

    # 実行
    if isCopter == True:
        initialMode = "GUIDED"
        vheicle.parameters[ 'AUTO_OPTIONS' ] = 3   # AUTOモードでtakeoffできるように
        print("set auto_options=3")

    else:
        initialMode = "MANUAL"

    vheicle.disarm()
    vheicle.mode = VehicleMode( initialMode )
    vheicle.wait_for_mode( initialMode )

    vheicle.armed = True
    vheicle.arm()
    print("ARMED.")

    vheicle.mode = VehicleMode("AUTO")
    vheicle.wait_for_mode("AUTO")
    print("mode = AUTO")

    print( "latest point:", latestLat, latestLon )

# print("land wait ...")
    if isBlock == False:
        return

    target = LocationGlobalRelative( latestLat, latestLon, 0 )
    while True:
        currenntPos = vheicle.location.global_relative_frame
        lastMeters = get_distance_metres( currenntPos, target )

        if lastMeters < 5:
            break

        print("last :", lastMeters )
        time.sleep( 1 ) 

###############################################################################
#   description :   mpのファイルを読み込む
#   function    :   mpReader
#   parameters  :   fileName,       ファイル名（mpから出力されたもの
#   return      :   command, lat, lon, alt のリスト
###############################################################################
def mpReader( FileName ):

    commands=[]
    lats=[]
    lons=[]
    alts=[]

    with open( FileName, 'r' ) as inFile:
        lines = inFile.readlines()

    nRow = 0
    for s in lines:
        list = s.split("\t")
        if nRow > 1:        # MPファイルは2行スキップ
            commands.append( int( list[3] ) )
            lats.append( float( list[8] ) )
            lons.append( float( list[9] ) )
            alts.append( float( list[10] ) )
        nRow = nRow + 1

    return ( commands, lats, lons, alts )


###############################################################################
#   description :   飛行機のお仕事
#                   NRT -> main
#   function    :   NRT2Main
###############################################################################
def plane_NRT2Main():
    AutoMove( conPlane,     planeWP1,   False,  True )

def plane_Main2NRT():
    AutoMove( conPlane,     planeWP2,   False,  True )

###############################################################################
#   description :   隣接のお仕事
#                   copter -> rover
#   function    :   rinsetsu
###############################################################################
def copter_rover_Main2Seven11():
    AutoMove( conCopter,    copterWP1,  True,   True )
    AutoMove( conRoverR,    roverRWP1,  False,  True )

def copter_rover_Seven112Main():
    AutoMove( conCopter,    copterWP2,  True,   False )
    AutoMove( conRoverR,    roverRWP2,  False,  False )

###############################################################################
#   description :   対岸のお仕事
#                   boat -> rover
#   function    :   taigan
###############################################################################
def boat_rover_Main2NamekawaSt():
    AutoMove( conBoat,      boatWP1,    False, True )
    AutoMove( conRoverT,    roverTWP1,  False, True )

def boat_rover_NamekawaSt2Main():
    AutoMove( conBoat,      boatWP2,    False, False )
    AutoMove( conRoverT,    roverTWP2,  False, False )

###############################################################################
#   description :   メイン
#                   NRT -> main port
#                   main port -> copter -> seven11
#                   main port -> boat -> Namekawa st.
###############################################################################
def automove_main():

    print("do automove_main")

    #threadP1 = threading.Thread( target = plane_NRT2Main )
    #threadP2 = threading.Thread( target = plane_Main2NRT )
    threadR1 = threading.Thread( target = copter_rover_Main2Seven11 )
    threadT1 = threading.Thread( target = boat_rover_Main2NamekawaSt )

    # # 飛行機のお仕事
    plane_NRT2Main()

    # 隣接,対岸
    threadR1.start()
    threadT1.start()


###############################################################################
#   description :   デバッグ用
###############################################################################
def automove_debug():

    print("do debug")

    # 1.Plane
    AutoMove( conPlane, planeWP1, False, True )
    #AutoMove( conPlane, planeWP2, False, True )

    # 2.Copter
    #AutoMove( conCopter, copterWP1, True, False )
    #AutoMove( conCopter, copterWP2, True, True )

    # 3.Boat
    #AutoMove( conBoat, boatWP1, False, False )
    #AutoMove( conBoat, boatWP2, False, True )

    # 4.RoberRinsetsu
    #AutoMove( conRoverR, roverRWP1, False, False )
    #AutoMove( conRoverR, roverRWP2, False, True )

    # 5.RoverTaigan
    #AutoMove( conRoverT, roverTWP1, False, False )
    #AutoMove( conRoverT, roverTWP2, False, True )

    time.sleep( 1 )

###############################################################################
#   description :   物流（を想定した）デモ
###############################################################################
# 接続先
conPlane    = "udp:127.0.0.1:14551"     # quad plane
conCopter   = "udp:127.0.0.1:14561"     # copter
conBoat     = "udp:127.0.0.1:14571"     # boat
conRoverR   = "udp:127.0.0.1:14581"     # 隣接rover
conRoverT   = "udp:127.0.0.1:14591"     # 対岸rover

# WPファイル, 1=往, 2=復
planeWP1    = "/home/ardupilot/ardupilot/dev-app/day5/plane_NRT2Main.txt"
planeWP2    = "/home/ardupilot/ardupilot/dev-app/day5/plane_Main2NRT.txt"
copterWP1   = "/home/ardupilot/ardupilot/dev-app/day5/copter_Main2Rinsetsu.txt"
copterWP2   = "/home/ardupilot/ardupilot/dev-app/day5/copter_Main2Rinsetsu.txt"
boatWP1     = "/home/ardupilot/ardupilot/dev-app/day5/boat_Main2Taigan.txt"
boatWP2     = "/home/ardupilot/ardupilot/dev-app/day5/boat_Taigan2Main.txt"
roverRWP1   = "/home/ardupilot/ardupilot/dev-app/day5/rover_Rinsetsu2Seven11.txt"
roverRWP2   = "/home/ardupilot/ardupilot/dev-app/day5/rover_Seven112Rinsetsu.txt"
roverTWP1   = "/home/ardupilot/ardupilot/dev-app/day5/rover_Taigan2St.txt"
roverTWP2   = "/home/ardupilot/ardupilot/dev-app/day5/rover_St2Taigan.txt"

automove_debug()     # デバッグ用
#automove_main()       # 自動
