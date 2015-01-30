

; The name of the installer
Name "Agent"
 
; installer properties
XPStyle on
 
; The file to write
OutFile "AgentInstaller.exe"

!define MUI_ICON "WDLogo.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "WDHeaderLogo.bmp"
!define MUI_HEADERIMAGE_BITMAP_STRETCH AspectFitHeight
!define MUI_HEADERIMAGE_RIGHT

BrandingText "WatchPoint Data"
 
; MUI Symbol Definitions
!include Sections.nsh
!include MUI2.nsh
!include LogicLib.nsh
!include "TextFunc.nsh"
!insertmacro MUI_LANGUAGE English

!macro ClearStack
    ${Do}
        Pop $0
        IfErrors send
    ${Loop}
send:
!macroend

!define ClearStack "!insertmacro ClearStack"
 
!include "WAgent.nsdinc"
 
Page custom fnc_AgentWelcomeDialog_Show

;In order to hide all the installation related details
;ShowInstDetails nevershow
;SetDetailsPrint none

!insertmacro MUI_PAGE_INSTFILES

Section
		
	InitPluginsDir	
	
	DetailPrint "Reading configuration parameters"
	
	File '/oname=$PluginsDir\config.properties' 'config.properties'
		
	${ConfigReadS} '$PluginsDir\config.properties' "Command=" $R0	
	${ConfigReadS} '$PluginsDir\config.properties' "CallbackFinishedUrl=" $R1	
	${ConfigReadS} '$PluginsDir\config.properties' "CallbackUnFinishedUrl=" $R2
	${ConfigReadS} '$PluginsDir\config.properties' "Param=" $R3
	
	Delete "$PluginsDir\config.properties"	

	DetailPrint "Starting Agent Installation"    
	
	File '/oname=$PluginsDir\WindowsAgentSetup.exe' 'WindowsAgentSetup.exe'
	ExecWait '"$PluginsDir\WindowsAgentSetup.exe" $R0' $0 
	
	DetailPrint "WindowsAgentSetup exit code = $0"	
	Delete "$PluginsDir\WindowsAgentSetup.exe"		
	
	DetailPrint "Posting Installation feedback to the server"
	
	StrCpy $R4 "param=$R3"
	StrCpy $R5 $0
	
	${ClearStack}	
	
	${If} $R5 != 0
		MessageBox MB_OK "Unable to complete Agent Installation. Error Code: $R5"		
		inetc::post "$R4" "$R2" "$PluginsDir\httpCallback.txt"
	${Else}	
		inetc::post "$R4" "$R2" "$PluginsDir\httpCallback.txt"			
	${EndIf}
	
	Pop $0		
	StrCmpS $0 "OK" success failedToSubmit
	
	failedToSubmit:	
		MessageBox MB_OK|MB_ICONEXCLAMATION "There was an error submitting your Installation Feedback"				
	Return
	
	success:	
		Delete "$PluginsDir\httpCallback.txt"
		MessageBox MB_OK|MB_ICONINFORMATION "Your Installation Feedback was successfully received"
				
SectionEnd