; 安装脚本

; 定义应用名称和版本
!define APPNAME "日志搜索工具"
!define APPVERSION "1.0"
!define COMPANYNAME "Your Company"
!define DESCRIPTION "一个简单的日志搜索工具"

; 包含现代界面
!include "MUI2.nsh"

; 设置应用名称
Name "${APPNAME}"

; 设置输出文件名
OutFile "LogSearchTool_Setup.exe"

; 默认安装目录
InstallDir "$PROGRAMFILES\${APPNAME}"

; 获取安装目录的注册表字符串（如果可用）
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; 请求应用程序权限
RequestExecutionLevel admin

;--------------------------------
; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "/Users/dee/Documents/Side/log_icon.ico"  ; 如果有图标文件，请替换为实际路径

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"  ; 如果有许可证文件，请替换为实际路径
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

;--------------------------------
; 安装部分
Section "安装" SecInstall
  SetOutPath "$INSTDIR"
  
  ; 添加文件
  File "dist\日志搜索工具.exe"
  
  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; 创建开始菜单快捷方式
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\日志搜索工具.exe"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\卸载 ${APPNAME}.lnk" "$INSTDIR\uninstall.exe"
  
  ; 创建桌面快捷方式
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\日志搜索工具.exe"
  
  ; 写入注册表信息
  WriteRegStr HKCU "Software\${APPNAME}" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\日志搜索工具.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
SectionEnd

;--------------------------------
; 卸载部分
Section "Uninstall"
  ; 删除安装的文件
  Delete "$INSTDIR\日志搜索工具.exe"
  Delete "$INSTDIR\uninstall.exe"
  
  ; 删除开始菜单快捷方式
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\卸载 ${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  ; 删除桌面快捷方式
  Delete "$DESKTOP\${APPNAME}.lnk"
  
  ; 删除安装目录
  RMDir "$INSTDIR"
  
  ; 删除注册表项
  DeleteRegKey HKCU "Software\${APPNAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd