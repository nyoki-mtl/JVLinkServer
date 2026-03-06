#include "core/jv_link_event_sink.h"

#include <spdlog/spdlog.h>

#include <iostream>

/**
 * コンストラクタ
 *
 * イベントハンドラーを受け取り、参照カウントを1に初期化する。
 *
 * @param handler JV-Linkイベントを処理するコールバック関数
 */
JVLinkEventSink::JVLinkEventSink(EventHandler handler) : m_refCount(1), m_handler(handler) {}

/**
 * デストラクタ
 */
JVLinkEventSink::~JVLinkEventSink() {}

/**
 * IUnknown::QueryInterfaceの実装
 *
 * サポートするインターフェースを問い合わせる。
 * IUnknown、IDispatch、IJVLinkEventsをサポートする。
 */
STDMETHODIMP JVLinkEventSink::QueryInterface(REFIID riid, void** ppvObject) {
  if (!ppvObject) {
    return E_POINTER;
  }

  if (IsEqualIID(riid, IID_IUnknown) || IsEqualIID(riid, IID_IDispatch) || IsEqualIID(riid, IID_IJVLinkEvents)) {
    *ppvObject = static_cast<IDispatch*>(this);
    AddRef();
    return S_OK;
  }

  *ppvObject = nullptr;
  return E_NOINTERFACE;
}

/**
 * IUnknown::AddRefの実装
 *
 * 参照カウントをインクリメントする。
 *
 * @return 新しい参照カウント
 */
STDMETHODIMP_(ULONG) JVLinkEventSink::AddRef() {
  return InterlockedIncrement(&m_refCount);
}

/**
 * IUnknown::Releaseの実装
 *
 * 参照カウントをデクリメントし、0になったらオブジェクトを削除する。
 *
 * @return 新しい参照カウント
 */
STDMETHODIMP_(ULONG) JVLinkEventSink::Release() {
  ULONG ulRef = InterlockedDecrement(&m_refCount);
  if (0 == ulRef) {
    delete this;
  }
  return ulRef;
}

/**
 * IDispatch::GetTypeInfoCountの実装
 *
 * タイプ情報の数を返す。この実装ではタイプ情報を提供しない。
 */
STDMETHODIMP JVLinkEventSink::GetTypeInfoCount(UINT* pctinfo) {
  // タイプ情報は提供しない
  *pctinfo = 0;
  return S_OK;
}

/**
 * IDispatch::GetTypeInfoの実装
 *
 * タイプ情報を取得する。この実装ではサポートされない。
 */
STDMETHODIMP JVLinkEventSink::GetTypeInfo(UINT, LCID, ITypeInfo** ppTInfo) {
  // タイプ情報は提供しない
  *ppTInfo = nullptr;
  return E_NOTIMPL;
}

/**
 * IDispatch::GetIDsOfNamesの実装
 *
 * 名前からDISPIDへのマッピングを行う。この実装ではサポートされない。
 */
STDMETHODIMP JVLinkEventSink::GetIDsOfNames(REFIID, LPOLESTR*, UINT, LCID, DISPID*) {
  // 名前からDISPIDへのマッピングはサポートしない
  return E_NOTIMPL;
}

/**
 * IDispatch::Invokeの実装
 *
 * JV-Linkからのイベント通知を処理する。
 * イベントは1つのBSTR引数を持ち、登録されたハンドラーに転送する。
 */
STDMETHODIMP JVLinkEventSink::Invoke(DISPID dispIdMember, REFIID, LCID, WORD wFlags, DISPPARAMS* pDispParams, VARIANT*,
                                     EXCEPINFO*, UINT*) {
  spdlog::debug("JVLinkEventSink::Invoke called - DISPID: {}, wFlags: {:#x}, cArgs: {}", dispIdMember, wFlags,
                pDispParams ? pDispParams->cArgs : 0);

  // メソッド呼び出しのみを処理
  if (wFlags != DISPATCH_METHOD) {
    spdlog::warn("JVLinkEventSink::Invoke - Not a method call, wFlags: {:#x}", wFlags);
    return E_INVALIDARG;
  }

  // JV-Linkイベントは1つのBSTR引数を持つ仕様
  if (pDispParams->cArgs != 1) {
    spdlog::error("JVLinkEventSink::Invoke - Expected 1 argument, but got {}", pDispParams->cArgs);
    std::wcerr << L"Expected 1 argument, but got " << pDispParams->cArgs << std::endl;
    return DISP_E_BADPARAMCOUNT;
  }

  if (pDispParams->rgvarg[0].vt != VT_BSTR) {
    spdlog::error("JVLinkEventSink::Invoke - Expected BSTR argument, got VT type: {:#x}", pDispParams->rgvarg[0].vt);
    std::wcerr << L"Expected BSTR argument" << std::endl;
    return DISP_E_TYPEMISMATCH;
  }

  BSTR bstrParam = pDispParams->rgvarg[0].bstrVal;
  std::wstring param(bstrParam, SysStringLen(bstrParam));
  spdlog::info("JVLinkEventSink::Invoke - Event received! DISPID: {}, param length: {}", dispIdMember, param.length());

  if (m_handler) {
    // 登録されたイベントハンドラーを呼び出す
    m_handler(dispIdMember, param);
  } else {
    spdlog::error("JVLinkEventSink::Invoke - No handler registered!");
  }

  return S_OK;
}