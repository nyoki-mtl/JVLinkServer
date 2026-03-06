#pragma once

#include <Windows.h>

#include <functional>
#include <string>

// oleview.exeで判明したイベントインターフェースのIID
// {17E1E656-828B-4849-B043-FA62B92D9E41}
const IID IID_IJVLinkEvents = {0x17E1E656, 0x828B, 0x4849, {0xB0, 0x43, 0xFA, 0x62, 0xB9, 0x2D, 0x9E, 0x41}};

// イベントハンドラの型定義
// 引数: イベントのDISPID, イベントパラメータ
using EventHandler = std::function<void(DISPID, const std::wstring&)>;

class JVLinkEventSink : public IDispatch {
 public:
  JVLinkEventSink(EventHandler handler);
  virtual ~JVLinkEventSink();

  // IUnknown methods
  STDMETHODIMP QueryInterface(REFIID riid, void** ppvObject) override;
  STDMETHODIMP_(ULONG) AddRef() override;
  STDMETHODIMP_(ULONG) Release() override;

  // IDispatch methods
  STDMETHODIMP GetTypeInfoCount(UINT* pctinfo) override;
  STDMETHODIMP GetTypeInfo(UINT, LCID, ITypeInfo** ppTInfo) override;
  STDMETHODIMP GetIDsOfNames(REFIID, LPOLESTR*, UINT, LCID, DISPID*) override;
  STDMETHODIMP Invoke(DISPID dispIdMember, REFIID, LCID, WORD wFlags, DISPPARAMS* pDispParams, VARIANT*, EXCEPINFO*,
                      UINT*) override;

 private:
  volatile LONG m_refCount;
  EventHandler m_handler;
};