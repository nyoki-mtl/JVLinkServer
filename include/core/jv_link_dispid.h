#pragma once

#include <Ole2.h>

/**
 * @file jv_link_dispid.h
 * @brief JV-Link COM interface DISPID constants
 *
 * All DISPID constants for JV-Link COM component interfaces.
 * These values are derived from JVDTLab.dll type library.
 */

namespace jvlink {
namespace dispid {

// =============================================================================
// Event DISPIDs for _IJVLinkEvents interface
// Used for COM event notifications from JV-Link
// =============================================================================
constexpr DISPID JVEVT_PAY = 0x1;            // JVEvtPay - 払戻確定
constexpr DISPID JVEVT_JOCKEY_CHANGE = 0x2;  // JVEvtJockeyChange - 騎手変更
constexpr DISPID JVEVT_WEATHER = 0x3;        // JVEvtWeather - 天候・馬場状態変更
constexpr DISPID JVEVT_COURSE_CHANGE = 0x4;  // JVEvtCourseChange - コース変更
constexpr DISPID JVEVT_AVOID = 0x5;          // JVEvtAvoid - 出走取消・競走除外
constexpr DISPID JVEVT_TIME_CHANGE = 0x6;    // JVEvtTimeChange - 発走時刻変更
constexpr DISPID JVEVT_WEIGHT = 0x7;         // JVEvtWeight - 馬体重発表

// =============================================================================
// Method DISPIDs for JV-Link COM interface
// Used for invoking JV-Link COM methods
// =============================================================================
constexpr DISPID JV_SET_SAVE_PATH = 0x1;        // JVSetSavePath - Sets save path
constexpr DISPID JV_INIT = 0x4;                 // JVInit - Initializes JV-Link
constexpr DISPID JV_CLOSE = 0x5;                // JVClose - Ends JV-Data reading processing
constexpr DISPID JV_SET_UI_PROPERTIES = 0x6;    // JVSetUIProperties - Changes settings via dialog
constexpr DISPID JV_OPEN = 0x7;                 // JVOpen - Requests acquisition of accumulated data
constexpr DISPID JV_STATUS = 0x8;               // JVStatus - Retrieves download progress information
constexpr DISPID JV_READ = 0x9;                 // JVRead - Reads JV-Data
constexpr DISPID JV_RT_OPEN = 0xA;              // JVRTOpen - Requests acquisition of real-time data
constexpr DISPID JV_CANCEL = 0xB;               // JVCancel - Stops the download thread
constexpr DISPID JV_FILE_DELETE = 0xC;          // JVFiledelete - Deletes downloaded files
constexpr DISPID JV_SET_SERVICE_KEY = 0xD;      // JVSetServiceKey - Changes JV-Link service key
constexpr DISPID JV_SET_SAVE_FLAG = 0xF;        // JVSetSaveFlag - Changes JV-Link save flag
constexpr DISPID JV_SKIP = 0x13;                // JVSkip - Skips reading JV-Data
constexpr DISPID JV_GETS = 0x16;                // JVGets - Reads JV-Data (byte array version)
constexpr DISPID JV_MV_PLAY = 0x17;             // JVMVPlay - JRA Racing Viewer race video playback
constexpr DISPID JV_MV_CHECK = 0x18;            // JVMVCheck - JRA Racing Viewer race video release check
constexpr DISPID JV_FUKU_FILE = 0x19;           // JVFukuFile - Requests racing uniform image (saves to file)
constexpr DISPID JV_FUKU = 0x1A;                // JVFuku - Requests racing uniform image (binary)
constexpr DISPID JV_MV_OPEN = 0x1B;             // JVMVOpen - Requests acquisition of video lists
constexpr DISPID JV_MV_READ = 0x1C;             // JVMVRead - Reads video lists
constexpr DISPID JV_MV_PLAY_WITH_TYPE = 0x1D;   // JVMVPlayWithType - JRA Racing Viewer video playback with type
constexpr DISPID JV_COURSE_FILE = 0x1E;         // JVCourseFile - Requests course map (with explanation)
constexpr DISPID JV_COURSE_FILE2 = 0x1F;        // JVCourseFile2 - Requests course map (file output)
constexpr DISPID JV_WATCH_EVENT = 0x21;         // JVWatchEvent - Starts event notification
constexpr DISPID JV_SET_PAY_FLAG = 0x22;        // JVSetPayFlag - Sets pay flag
constexpr DISPID JV_WATCH_EVENT_CLOSE = 0x23;   // JVWatchEventClose - Ends event notification
constexpr DISPID JV_MV_CHECK_WITH_TYPE = 0x24;  // JVMVCheckWithType - JRA Racing Viewer video release check with type

// =============================================================================
// Property DISPIDs for JV-Link COM interface
// Used for getting/setting JV-Link COM properties
// =============================================================================

// Property getters
constexpr DISPID GET_SAVE_PATH = 0x2;                // m_savepath property getter
constexpr DISPID GET_SERVICE_KEY = 0x3;              // m_servicekey property getter
constexpr DISPID GET_SAVE_FLAG = 0xE;                // m_saveflag property getter
constexpr DISPID GET_JV_LINK_VERSION = 0x10;         // m_JVLinkVersion property getter
constexpr DISPID GET_TOTAL_READ_FILE_SIZE = 0x11;    // m_TotalReadFilesize property getter
constexpr DISPID GET_CURRENT_READ_FILE_SIZE = 0x12;  // m_CurrentReadFilesize property getter
constexpr DISPID GET_CURRENT_FILE_TIMESTAMP = 0x14;  // m_CurrentFileTimeStamp property getter
constexpr DISPID GET_PAY_FLAG = 0x20;                // m_payflag property getter

// Property setters
constexpr DISPID PUT_PARENT_HWND = 0x15;  // ParentHWnd property setter

}  // namespace dispid
}  // namespace jvlink
