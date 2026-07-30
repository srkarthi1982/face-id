# DEVICE LAN VERSION INTERFACE DOCUMENT V5.1.14

## API Endpoints Reference

> **Base URL:** `http://<Device IP>:8090`
> **All interfaces are accessed via HTTP. Device password is used as the security key.**
> **Response format includes:** `result`, `success`, `msg`, `code`, and `data`

## II. Device Management


### 2.1 Device Password Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setPassWord`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate request type of media | String | Y | application/x-www-form-urlencoded
| oldPass | Old password | String | Y | For new devices or the reset (initialized) devices, set initialization password 
| newPass | New password | String | Y | For new devices or the reset (initialized) devices, set initialization password 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "password is : test1234", //Device password, also called as Interface calling password, please keep properly. If password forgot, need to reset the device, and all data will be cleared "msg": "Password set successfully", "result":1,//Interface called "success":true//Device password set successfully

**Response Format:**


### 2.2 Device Serial Number Query

**Method:** `POST/GET` | **URL:** `http://DeviceIP:8090/getDeviceKey`

**Notes:** Request data Attention: Calling this Interface does not require passing in parameters and pass, GET or POST method can call successfully. Postman example Return example { "code":"LAN_SUS-0", "data":"84E0F420893301FA", "msg": "Interface called", "result":1, "success":true }

**Response Format:**


### 2.3 Device Configuration Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Pass in config {}, restore all device configuration parameters to default values
| config | Collection of device configuration | JSON | Y | Pass in config {}, restore all device configuration parameters to default values
| Voice broadcast configuration | Voice broadcast configuration |  |  | 
| ttsEnable | Int | Voice broadcast switch;\|1. Off\|2. On (by default) |  | 
| ttsModType | Int | Voice broadcast type (Verification succeeded)\| Domestic: \|1. Broadcast name (default)\|2. Not broadcast\|100. Custom\| Overseas:\|1. Broadcast recognition succeeded\|2.Off |  | 
| ttsModContent | String | Voice broadcast custom content (Verification succeeded)\|If ttsModType is 100, this field is required and cannot be empty\|Allowed tags: Name {name}, personnel remarks {tag}. The field format is fixed, other content only allows numbers, English and Chinese characters, with the length limit of 60 characters.\|For example: {name} welcome\|  Overseas: This field is deprecated |  | 
| ttsModStrangerType | Int | Voice broadcast type (Stranger)\| Domestic:\|1. The person is not registered, please contact the administrator (by default)\|2. Not broadcast\|100. Custom\| Overseas:\|1. Broadcast the person is not registered\|2. Off |  | 
| ttsModStrangerContent | String | Broadcast the custom content (Stranger)\|If ttsModStrangerType is 100, this field is required and cannot be empty\|Only numbers, English and Chinese characters are allowed for the content, with the length limit of 60 characters. eg: Attention, stranger\| Overseas: This field is deprecated |  | 
| recNoPerTtsModeType | Int | Voice broadcast type (Permission denied)\|1. Not in pass time (default)\|2. Not broadcast\|100. Customize (No analysis for overseas devices, customize) |  | 
| recNoPerTtsModeContent | String | Broadcast the custom content (Permission denied)\|If recNoPerTtsModeType is 100, this field is required and cannot be empty\|Allowed tags: Name {name}, personnel remarks {tag}. For example: {name} has no permission to pass\|Other content only allows numbers, English and Chinese characters, with the length limit of 60 characters.\| Overseas: This field is deprecated |  | 
| touchTone | Int | For overseas device only\|If the touch screen has a sound\|1.Off\|2.On (Default) |  | 
| Verification Result Display | Verification Result Display |  |  | 
| displayModType | Int | Top-row text prompt mode (Verification succeeded)\|1. Name (Domestic default)\|2. Not display\|3. Display User No. Only supported by overseas devices\|100. self-defining |  | 
| displayModContent | String | The top-row text prompts custom content (Verification succeeded) \|If displayModType is 100, this field is required and cannot be empty \|Allowed tags: Name {name}, Personnel Remarks {tag}, Personnel number {id}. Such as: {name}, sign-in succeeded! \|Other content only allows numbers, Chinese and English and Chinese and English symbols, with the length limit of 60 characters. |  | 
| recSucDisplayText2Type | Int | Sub-row text prompt mode (Verification succeeded)\|1. Verification succeeded (by default) \|2. Not display\|100. Custom |  | 
| recSucDisplayText2Content | String | The sub-row text prompts custom content (Verification succeeded) \|If recSucDisplayText2Type is 100, this field is required and cannot be empty\|Allowed tags: Name {name}, Personnel Remarks {tag}, Personnel number {id}. Such as: {name}, sign-in succeeded! \|Personnel id{personId} For overseas device only\|The length is limited to 60 characters. |  | 
| displayModStrangerType | Int | Top-row text prompt mode (Stranger)\|1. Person not registered (by default)\|2. Not display\|100. Custom |  | 
| displayModStrangerContent | String | The top-row text prompts custom content (stranger) \|If displayModStrangerType is 100, this field is required and cannot be empty \|Tags are not supported. For example: Attention, strangers! \|The length is limited to 60 characters. |  | 
| displayModStranger2Type | Int | Sub-row text prompts mode (Stranger)\|1. Please contact admin (by default)\|2. Not display\|100. Custom |  | 
| displayModStranger2Content | String | Sub-row text prompts custom content (Stranger)\|If displaymodstranger2type is 100, this field is required and cannot be empty\|Tags are not supported. Such as: Attention, strangers!\|The length is limited to 60 characters. |  | 
| recNoPerDisplayText1Type | Int | Top-row text prompts mode (Permission denied)\|1. Name (Domestic default)\|2. Not display\|3. User ID Only supported by overseas devices\|100. Custom |  | 
| recNoPerDisplayText1Content | String | Top-row text prompts custom content (Permission denied)\|If recNoPerDisplayText1Type is 100, this field is required and cannot be empty\|Allowed tags: Name {name}, Personnel Remarks {tag}, Personnel number {id}. For example: {name}, no permission to access!\|The length is limited to 60 characters. |  | 
| recNoPerDisplayText2Type | Int | Sub-row text prompts mode (Permission denied)\|1. Not in passtime (by default)\|2. Not display\|100. Custom |  | 
| recNoPerDisplayText2Content | String | Sub-row text prompts custom content (Permission denied)\|If recnoperdisplaytext2type is 100, this field is required and cannot be empty\|Allowed tags: Name {name}, Personnel Remarks {tag}, Personnel number {id}. For example: {name}, no permission to access!\|The length is limited to 60 characters. |  | 
| Input&Output Configuration | Input&Output Configuration |  |  | 
| baudRateModeType232 | Int | 232 serial port baud rate\|1.9600 (by default)\|2.19200\|3.38400\|4.57600\|5.115200 |  | 
| comModType | Int | 232 Serial port output type (Verification succeeded)\|1.Door opening command (by default)\|2.Not output\|4.Output Card No.\|∙ 100.Self-defining |  | 
| comModContent | String | 232 serial port outputs custom content (Verification succeeded)\|If comModType is 100, this field is required and cannot be empty\|Allowed tags: Phone Number {phone}, Personnel Number {id},  Card Number Decimal {idcardNum}, Card Number Hexadecimal {idcardNumHex}, Personnel Remarks {tag}, Personnel Remarks Hexadecimal {tagHex}\|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, numbers, Wiegand\|\|Card swiping board\|\|Supported Wiegand types: Wiegand 24, Wiegand 26, Wiegand 32, Wiegand 34, Wiegand 40, Wiegand 42, Wiegand 48, Wiegand 50, Wiegand 56, Wiegand 58, Wiegand 64, Wiegand 64,Wiegand 66\|Wiegand type samples:\|Wiegand 26: #26WG{ idcardNum }#\|Wiegand 34: #34WG123456#\|Wiegand 50: #50WG{ idcardNum }#\|Wiegand 66: #66WG{ idcardNum }#\|Note: { idcardNum } + numbers, combined content output range:\|Range all within 0x1 – 2 wiegand numerical power\|For example:\|Wiegand 26 range: 0x01-0xFFFFFF.\|Wiegand 34 range: 0x01-0xFFFFFFFF.\|Wiegand 50 range: 0x01-0xFFFFFFFFFFFF.\|Wiegand 66 range: 0x01-0xFFFFFFFFFFFFFFFF. |  | 
| serialOutMode | Int | 232 serial output type (Stranger)\|2. Not output (by default)\|100. Custom |  | 
| serialOutContent | String | 232 serial port output custom content (Stranger)\|If serialOutMode is 100, this field is required and cannot be empty.\|Tags are not supported.\|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, and numbers.\|Custom content incoming format: such as Wiegand 26: #26WG123#\|Wiegand card swiping board @see comModContent |  | 
| recNoPerComModeType | Int | 232 serial port output type (Permission denied)\|2. Not output (by default)\|100. Self-defining\|Note: 2.0 compatible (open door output excluded) |  | 
| recNoPerComModeContent | String | 232 serial port output custom content (Permission denied)\|If recNoPerComModeType is 100, this field is required and cannot be empty.\|Allowed tags: Phone Number {phone}, Personnel Number {id},  Card Number Decimal {idcardNum}, Card Number Hexadecimal {idcardNumHex}, Personnel Remarks {tag}, Personnel Remarks Hexadecimal {tagHex}\|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, and numbers. Wiegand\|Card swiping board @see comModContent |  | 
| baudRateModeType485 | Int | 485 Serial port baud rate\|1.9600 (by default)\|2.19200\|3.38400\|4.57600\|5.115200 |  | 
| comModType485 | Int | 485 serial port output type (Verification succeeded)\|2. Not output (by default)\|100. Custom |  | 
| comModContent485 | String | 485 serial port output custom content (Verification succeeded)\|If comModType485 is 100, this field is required and cannot be empty\|Allowed tags: Phone Number {phone}, Personnel Number {id},  Card Number Decimal {idcardNum}, Card Number Hexadecimal {idcardNumHex}, Personnel Remarks {tag}, Personnel Remarks Hexadecimal {tagHex} \|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, and numbers. |  | 
| serialOutMode485 | Int | 485 serial port output type (Stranger)\|2. Not output (by default)\|100. Custom |  | 
| serialOutContent485 | String | 485 serial port output custom content (Stranger)\|Tags are not supported. \|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, and numbers. |  | 
| recNoPerComModeType485 | Int | 485 serial port output type (Permission denied)\|2. Not output (by default)\|100. Custom |  | 
| recNoPerComModeContent485 | String | 485 serial port output custom content (Permission denied)\|If recNoPerComModeType485 is 100, this field is required and cannot be empty.  \|Allowed tags:Phone Number {phone}, Personnel Number {id},  Card Number Decimal {idcardNum}, Card Number Hexadecimal {idcardNumHex}, Personnel Remarks {tag}, Personnel Remarks Hexadecimal {tagHex}\|The length is limited to 60 characters, including but not limited to Chinese and English, special symbols, and numbers. |  | 
| recSucWiegandType | Int | Wiegand output type (Verification succeeded)\|1. Not output\|2. Wiegand 26 (by default)\|3. Wiegand 34 \|4. Wiegand 50 \|5. Wiegand 66\|6. Wiegand 24 \|7. Wiegand 32 \|9. Wiegand 40 \|10. Wiegand 42\|11. Wiegand 48 \|12. Wiegand 56 \|13. Wiegand 58 \|14. Wiegand 64 |  | 
| recSucWiegandContent | String | Wiegand output custom content (Verification succeeded)\|Allowed tags: Card Number Decimal {idcardNum}, Personnel Number {id} and numbers.\|Output range @see comModContent |  | 
| recFailWiegandType | Int | Wiegand output type (Stranger)\|1. Not output(by default) \|2. Wiegand 26  \|3. Wiegand 34  \|4. Wiegand 50 \|5. Wiegand 66\|6. Wiegand 24 \|7. Wiegand 32 \|9. Wiegand 40\|10. Wiegand 42 \|11. Wiegand 48 \|12. Wiegand 56\|13. Wiegand 58 \|14. Wiegand 64 |  | 
| recFailWiegandContent | String | Wiegand output custom content (Stranger)\|Tags are not supported, only numbers are allowed\|Output range @see comModContent |  | 
| recNoPerWiegandType | Int | Wiegand output type (Permission denied)\|1. Not output (Domestic default)\|2. Wiegand 26 (Overseas Defaul)\|3. Wiegand 34\|4. Wiegand 50\|5. Wiegand 66\|6. Wiegand 24 \|7. Wiegand 32 \|9. Wiegand 40 \|10. Wiegand 42 \|11. Wiegand 48 \|11. Wiegand 56 \|13. Wiegand 58 \|14. Wiegand 64 |  | 
| recNoPerWiegandContent | String | Wiegand output custom content (Permission denied)\|Only tags are allowed: Card Number Decimal {idcardNum}, Personnel Number {id} and numbers\|Output range @see comModContent |  | 
| delayTimeForCloseDoor | Int | Opening time\|500ms (by default)\|The duration of the relay opening, in ms.\|Please enter an integer between 100-25500, and round down to hundreds, such as 111—>100. |  | 
| switchPlan | Json | Relay normally open and closed time period setting: \|week on behalf of the week index (such as 0-Monday, 1-Tuesday, ...6-Sunday), time for the time period. .6-Sunday), time for the time period\|Json example:\|[{"week":1, "time": "09:00:00,10:00:00,17:00:00,17:30:00,18:30:00,20:25:00"}, {"week":2, "time": "09:00:00,10:00:00,17:00:00,17:30:00,18:30:00,20:25:00"}\|Range [00:00:00,23:59:59], based on time on the device Time segment format (startTime,endTime English comma separated): 09:00:00,11:00:00,13:00:00,15:00:00,17:00:00,19:00:00\|time can be set up to 6 segments, if only 1 segment is set up, then the latter segments will not be transmitted, such as: 09:00:00,11:00:00\|Each setting will overwrite the last information |  | 
| switchMode | Int | Relay Mode\|0 : Normally closed 1 : Normally open 2 : Normal mode (default)\|Normal mode does not need to set switchPlan, even if it is set, it will not take effect.\|Normally open/normally closed will be executed according to the corresponding time period after switchPlan is set, if not set, it will automatically take effect according to the whole time period every day. |  | 
| delayTimeForOpenDoor | Int | Relay Delayed Opening time\|0ms (by default)\|Delay n ms to open relay,in ms\|Please enter an integer between 0-25500, and round down to hundreds, such as 111->100. |  | 
| isOpenRelay | Int | Relay output switch (verification succeeded)\|1. On (by default)\|2. Off |  | 
| relaySwitch | Int | Relay output type (stranger)\|1. On\|2. Off (by default) |  | 
| recNoPerRelayType | Int | Relay output switch (Permission denied)\|1. On\|2. Off (by default) |  | 
| isIDCardPositive | Int | 1: Card reading and card number output in normal order (default)\|2: Card reading and card number output in reverse order |  | 
| Recognition Parameters | Recognition Parameters |  |  | 
| isRecognitionOpen | Int | Face&Card comparison switch\|1. Off\|2. On (by default) |  | 
| multiplayerDetection | Int | Face detection type\|1. Multi-person recognition (by default)\|2. Single-person recognition |  | 
| recRank | Int | Live detection switch (Recognition level)\|1. Off\|3. On (by default) |  | 
| isSimilarEnable | Int | Photo similarity comparison switch\|After enabled, the face registration will conduct similarity comparison. For the same person ID, non-personal photos cannot be registered. After disabled, the registration of non-personal photos is allowed for the same person\|1. Off\|2. On (by default) |  | 
| identifyDistance | Int | Recognition distance (unit: cm) (2.0 compatible)\|Range: 30-200 (progressive by 10). There are differences for different devices, and the actual situation shall prevail.\|Default maximum value, there are differences for different devices, and the actual situation shall prevail. |  | 
| recDoubleValue | Int | 1: 1 threshold (Card & Face verification (Face&Card), face&card comparison)\|50 (by default)\|Tip: Please enter an integer between 0 and 100. The higher the score, the higher the recognition accuracy, but the recognition speed will slow down. |  | 
| identifyScores | Int | 1: N threshold (Face recognition score threshold) (2.0 compatible recCardFaceValue)\|Range 0-100 integer\|80 (by default)\|The higher the score, the higher the recognition accuracy, but the recognition speed will slow down. |  | 
| saveIdentifyTime | Int | Record deduplication (in seconds)\|60s (by default)\|Attention: Domestic device range 0-60\|Attention: Overseas device range 0-86400 |  | 
| recStrangerType | Int | Stranger warning switch\|1. Off\|2. On (by default) |  | 
| recStrangerTimesThreshold | Int | Number of stranger judgments\|3 (by default)\|Range: 1-20 integers\|Enable recstrangertype, which is valid; If the score threshold is not reached for N consecutive comparisons, it is determined as recognition failure;\|The larger the value, the longer the judgment time and the higher the accuracy. |  | 
| repeatRegEnable | Int | Continuous recognition switch\|1: Off\|2: On (by default) |  | 
| regInterval | Int | Continuous recognition interval\|Setting range: 2000~25500ms\|Default: 2000ms |  | 
| recType | Int | Recognition mode\|1. Local recognition\|2. Cloud recognition (The baseline is not supported temporarily) |  | 
| recModeIdcardScene |  | Face&Card verification mode\|1: Off (by default)\|2: All\|3: Strangers only\|4: Database personnel only |  | 
| uniquenessRegImage | Int | The uniqueness of registration photo\|1: Off\|2: On (by default)\| Attention: Only overseas device attributes are supported |  | 
| uniquenessRegCard | Int | The uniqueness of registration card\|1: off\|2: On (default)\|Attention:Only overseas device attributes are supported |  | 
| uniquenessFinger | Int | The uniqueness of registered fingerprint\|1: Off\|2: On (by default) \| Attention: Only overseas device attributes are supported |  | 
| manualFaceEnable | bool | Manual Face Recognition\|true: On\|false: off |  | 
| defendModeEnable |  | Defense Mode Switch\|1: Off\|2: On (default) |  | 
| attackCount |  | Attack Count Threshold\|Range: 5–100\|Default: 5 |  | 
| punishTime |  | Penalty Time\|Range: 2–60 minutes\|Default: 2 minutes |  | 
| On-site photo parameters | On-site photo parameters |  |  | 
| recSucSaveSpotImage | Int | On-site photo save switch (Verification succeeded)\|1. Off\|2. On (by default) |  | 
| recFailSaveSpotImage | Int | On-site photo save switch (Stranger)\|1. Off (by default)\|2. On |  | 
| recNoPerSaveSpotImage | Int | On-site photo save switch (Permission denied)\|1. Off (by default)\|2. On |  | 
| recDisplayImageMode | Int | Verification result displays photo settings\|1: On-site photo (by default)\| for overseas device only\|3: Not display |  | 
| Screen display parameters | Screen display parameters |  |  | 
| companyName | String | Company name\|The length is limited to 60 characters\|Default: Face Recognition System |  | 
| deviceName | String | Device name\|There is no display on the device UI, and the name displayed when the gadget (face device debugging facetool) searches the device\|The length is limited to 60 characters\|Default: Please enter the device name / factory model |  | 
| screenSaverTime | Int | Enter screen saver time\|Unit: second (180s by default)\|Integer of 60-300 |  | 
| showIp | Int | Whether to display IP\|1. Hide\|2. Display (by default) |  | 
| showDeviceKey | Int | Whether to display the device serial number\|1: Hide\|2: Display (by default) |  | 
| showPeopleNum | Int | Whether to display the number of people\|1: Hide\|2: Display (by default) |  | 
| showDeviceVersion | Int | Whether to display the device software version number\|1: Hide\|2: Display (by default) |  | 
| setButtonEnable | bool | Whether to show the setup button\|true : Display (default)\|false : No |  | 
| show4G | bool | Whether to display 4G card number\|true : Display (default)\|false : No |  | 
| Hardware Settings | Hardware Settings |  |  | 
| audioVolume | Int | Volume\|Default 100\|Integer from 0-100 |  | 
| antiTamper | Int | Device Anti-tamper Switch Enable\|1: Off\|2: On (by default) |  | 
| Registration Related | Registration Related |  |  | 
| saveRegisterPhoto | Int | Whether or not registration portraits save registration photos\|1: Off\|2: On (default)\|After closing, the registration photo will not be saved, and subsequent upgrades (algorithm) may cause the person to be unable to be recognized normally, so please choose carefully! |  | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "antiTamper": 2, "comModContent": "hello", ...... }, "msg": "Set successfully", "result": 1, "success": true } Parameter specification

**Response Format:**


### 2.4 Device Configuration Query

**Method:** `GET` | **URL:** `http://Device IP:8090/device/config`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 

**Notes:** Request data Query domain Postman example Return example { "code":"LAN_SUS-0", "data": { "applicationName": "", "comModContent": "hello", ... "isRecognitionOpen":1 }, "msg": "Set successfully", "result": 1, "success": true } Return specification It is consistent with the content returned by the device configuration setting interface. Attention: When using GET request, parameter is put in url, "#" 

**Response Format:**


### 2.5 Logo Change

**Method:** `POST` | **URL:** `http://Device IP:8090/changeLogo`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| imgBase64 | Base 64 code strings of logo image | String | Y | Without the header, for example: data: image/jpg; base64,\|Pass in -1 to clear im

**Response Format:**


### 2.6 Img1 Change

**Method:** `PUT` | **URL:** `http://Device IP:8090/device/img1`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| base64 | Base 64 code string of img1 | String | Y | Without the header, Such as: data: i mage/jpg; base64,\|Pass in -1 to clear img1 

**Response Format:**


### 2.7 Wired Network Configuration

**Method:** `POST/GET` | **URL:** `http://Device IP:8090/setNetInfo`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| isDHCPMod | Select DHCP mode | Int | Y | Device is in DHCP mode by default, which automatically obtains the IP address\|Pa
| ip | ip address | String | N/Y | Pass in ip field name in lower case, ip cannot be greater than 255
| gateway | Gateway | String | N/Y | 
| subnetMask | Subnet mask | String | N | 
| DNS | DNS server | String | N/Y | 

**Response Format:**


### 2.8 Wireless Network Configuration

**Method:** `POST` | **URL:** `http://Device IP:8090/setWifi`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| wifiMsg | Collection of wireless configuration information | Json | Y | Example of Json:\|Auto obtain IP\|{"ssId":"TP-LINK_E2.4G","pwd":"test-1234","isDHC

**Response Format:**


### 2.9 Device Time Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setTime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| timestamp | Unix millisecond timestamp | String | Y | After configured successfully, device will refresh its time (refresh every minut

**Response Format:**


### 2.10 Device Restarting

**Method:** `POST` | **URL:** `http://Device IP:8090/restartDevice`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Response Format:**


### 2.11 Device Resetting

**Method:** `POST/PUT` | **URL:** `http://Device IP:8090/device/reset`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| delete | Select to delete | Boolean | Y | Delete all recognition records, registration photos, on-site photos, personnel i

**Response Format:**


### 2.12 Device Upgrade

**Method:** `PUT` | **URL:** `http://Device IP:8090/ device/upgrade`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | URL of downloading OTA upgrade package | String | Y | Access this url when calling the Interface, if url can be accessed, then device 

**Response Format:**


### 2.13 Recognition Call-back

**Method:** `POST` | **URL:** `http://Device IP:8090/setIdentifyCallBack`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| callbackUrl | Call-back address | String | Y | When the device recognizes person successfully, it will send following fields to
| base64Enable | base64 switch of on-site photos | Int | N | 1: Off (by default) 2: On
| aliveType | String | Live detection judgment result\|1: Live detection succeeded\|2: Live detection failed\|3: Not judged | "aliveType":"2" | 
| base64 | String | On-site photo base64 code | "Base64": "Base64 encoded string" | 
| data | String | ID card information\|\|Address: home address,\|Birthday: date of birth,\|Compareresult: comparison result,\|Createtime: recognition time,\|Id: meaningless,\|Idnum: ID card number,\|IssuingOrgan: place of issue,\|Name: name,\|Nation: nation,\|Sex: gender,\|UsefulLife: validity of ID card | "data":"{\|\|"Address": "No. XX, XX District, XX village, XX town, XX City, Zhejiang Province",\|"birthday": "1995-11-22",\|"compareResult": false,\|"createTime": 1600426322501,\|"id": 0,\|"idNum": "33108119000000000",\|"issuingOrgan": "XXX",\|"name": "XXX",\|"nation": "Han",\|"sex": "male",\|"usefulLife": "2012.02.12-2022.02.12"\|}" | 
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| idcardNum | String | Corresponding idcardNum of personId | "idcardNum":"0380949491" | 
| identifyType | String | Comparison result\|1: Comparison succeeded\|2: Comparison failed\|3: Not compared | "type":"1" | 
| ip | String | Current IP address of the device | "ip":"192.168.20.66" | 
| model | String | Recognition mode\|0: Face recognition\|1: Face&Card double verification (Face&Card)\|2: Face&Card comparison\|3: Card verification\|4: Exit button (Signal)\|5: Remote verification\|6: Password verification\|7: Face&Password double verification\|8: QR code verification\|9: Fingerprint comparison\|10: QR code and face verification\|11: Card and password verification\|12: ID verification\|13: Face & Fingerprint Verification\| Note: mode 2/12 is not available overseas, and mode 8/10/11/13 only supports overseas devices | " model ":"1" | 
| passTimeType | String | Schedule judgement\|1: Within the schedule \|2: Out of the schedule\|3: Not judged | "passTimeType":"3" | 
| path | String | Path of photo storage | "path":"/data/record/IdentifyRecords/2021-12-28/17/170352_163_ef93cf4c265f41d9860ed356f6c1ea4b_rgb.jpg" | 
| permissionTimeType | String | Permission time judgement\|1: Within the time\|2: Out of the time\|3: Not judged | "permissionTimeType":"3" | 
| personId | String | 1.Person ID\|2.STRANGERBABY (Stranger)\|3.Face&Card comparison:IDCARD | "personId":"STRANGERBABY" | 
| recType | Int | Recognition method\|1: Local recognition\|2: Cloud recognition | "recType": 1 | 
| Time | String | Recognition record millisecond timestamp (subject to the device time) | "time":"1537236693823" | 
| dstOffset | Int | Daylight saving time offset (seconds)\|Such as: 3600 daylight saving time increased by 1h\|    0 Daylight saving time is not turned on | " dstOffset ": 3600 | 
| passbackTriggerType | Int | Anti-passback trigger type:\|0 no anti-passback triggered\|1 trigger anti-passback\|2 trigger into anti-passback | "passbackTriggerType": 1 | 
| maskState | int | Mask status\|1 wear a mask\|2 Not wearing a mask\|3 masks not tested | "maskState"  : 3 | 
| workCode | string | Work code | "workCode":"93675B" | 
| attendance | string | attendance status | "attendance":"1" | 
| type | String | Recognition method_Type of personnel\|\|Recognition method: \|face/faceAndcard/idcard/card/finger/idNumber/password/qrCode/faceAndQrCode/cardAndPassword/openDoor/remoteDoor/faceAndFinger\|\|Type of person:\|0: Within period \|1: Out of period\|2: Stranger/Recognition failed | face_0 (Face recognition, this person is within passtime)\|face_1 (Face recognition, and this person is not within passtime)\|face_2 (Face recognition/Mask detection, recognition failed/Mask detection failed)\|card_0 (Card recognition, this person is within passtime)\|card_1 (Card recognition, this person is not within passtime)\|card_2 (Card recognition, recognition failed)\|faceAndcard_0 (Double authentication, this person is within passtime)\|faceAndcard_1 (Double authentication, result of Card recognition is that this person is not within passtime)\|faceAndcard_2 (Double authentication, recognition failed)\|idcard_0 (Face&Card comparison, this person is within passtime)\|idcard_1 (Face&Card comparison, this person is not within passtime)\|idcard_2 (Face&Card comparison, recognition failed)\|password_0 (Password identification, and the person is within the passtime permission time)\|password_1 (Password identification, and the person is outside the passtime permission time)\|password_2 (Password verification, verification failed)\|finger_0 (Fingerprint identification, and the person is within the passtime permission time)\|finger_1 (Fingerprint identification, and the person is outside the passtime permission time)\|finger_2 (Fingerprint recognition, recognition failed)\|idNumber_0 (ID card identification, and the person is within the passtime permission time)\|idNumber_1 (ID card identification, and the person is outside the passtime permission time)\|idNumber_2(ID card identification, and the identification failed)\|qrCode_0 (QR code identification, and the person is within the passtime permission time)\|qrCode_1 (QR code identification, and the person is outside the passtime permission time)\|qrCode_2 (QR code identification, and the identification failed)\|faceAndQrCode_0 (Face&QR code verification, verification success)\|faceAndQrCode_1 (Face&QR code identification, and the person is outside the passtime permission time)\|faceAndQrCode_2 (Face&QR code verification, verification failed)\|cardAndPassword_0 (Card&Password verification, verification success)\|cardAndPassword_1 (Card&Password identification, and the person is outside the passtime permission time) | 

**Response Format:**


### 2.14 Registration Photo Callback

**Method:** `POST` | **URL:** `http://Device IP:8090/setImgRegCallBack`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Call-back address | String | Y | Pass in null content to clear call-back addresses, then successful recognition w
| base64Enable | base64 switch of on-site photos | Int | N | 1: Off (by default) 2: On
| deviceKey | String | Exclusive ID code of device |  | 
| personId | String | Person id |  | 
| time | String | Timestamp |  | 
| imgPath | String | Photo path (ftp path is incomplete, old-version parameter), for example: "imgPath":"/faceRegister/002_ad8c1119bd3c473d838de5d80ce389c9.jpg" |  | 
| newImgPath | String | Photo path (ftp path is incomplete, latest-version parameter), for example: "newImgPath":"ftp://192.168.1.224:8010/faceRegister/002_ad8c1119bd3c473\|d838de5d80ce389c9.jpg" |  | 
| path | String | Keep same with newImgPath |  | 
| faceId | String | Photo id |  | 
| ip | String | Device IP address |  | 
| feature | String | Feature code |  | 
| featureKey | String | Feature secret-key, this field is required to verify the validity when registering via feature code |  | 
| SDKVersion | String | Feature code in device algorithm version |  | 
| base64 | String | Base64 encoded string of the photo, without header, such as: data:image/jpg;base64 |  | 

**Response Format:**


### 2.15 Heartbeat Call-back

**Method:** `POST` | **URL:** `http://Device IP:8090/setDeviceHeartBeat`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Call-back address | String | Y | Device will POST fields: deviceKey, time, ip, personCount, faceCount, version, f
| Interval | Heartbeat Interval (unit in second) | Int | N | Not pass in or pass in null, heartbeat Interval will be 60s by default\|Suggested
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Millisecond timestamp of device current time | "time":"1537236693823" | 
| ip | String | Current device IP address | "ip":"192.168.20.66" | 
| personCount | String | Number of people in the device | "personCount":"2" | 
| faceCount | String | Number of photos in the device | "faceCount":"3" | 
| fingerCount | String | Number of fingerprintss in the device | " fingerCount":"3" | 
| version | String | Device serial number | "version":"3.6203" | 
| freeDiskSpace | String | Free space of Disk, unit: M | "freeDiskSpace":"4546.56" | 
| cpuUsageRate | String | CPU usage rate, unit: % | "cpuUsageRate":"46.206898" | 
| cpuTemperature | String | CPU temperature, unit: ℃ | "cpuTemperature":"76.0" | 
| memoryUsageRate | String | Memory usage rate, unit: % | "memoryUsageRate":"76.206898" | 
| deviceName | String | Device name | "deviceName":"Real Intelligent" | 
| SDKVersion | String | Version number of device algorithm | "SDKVersion":"v0.13.11.e2989-1180907.256-20190613-general.2.0.5.0" | 
| companyName | String | Company Name | "companyName":"face identification system" | 

**Response Format:**


### 2.16 Call-back Address Query

**Method:** `GET` | **URL:** `http://Device IP:8090/device/callback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Response Format:**


### 2.17 Remote Control Output

**Method:** `POST` | **URL:** `http://Device IP:8090/device/openDoorControl`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| type | Interaction type of device | Int | N | 1: Relay opening 2: 232 serial port 3: Wiegand 4: Custom text pop-up, custom voi
| content | Output content | String | N | type=2 or 5: serial port, with a length limit of 60 characters, including but no

**Response Format:**


### 2.18 Card Number Registration Call-back Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setCardRegCallBack`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Call-back address | String | Y | When the card number is registered successfully (including device enrolling card
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Device time when photo registered (millisecond timestamp) | "time":"1537236693823" | 
| ip | String | Current device IP address | "ip":"192.168.20.66" | 
| personId | String | Corresponding person id of card number registration | "personId":"abcd" | 
| idcardNum | String | Registered card number | "idcardNum":"360080" | 

**Response Format:**


### 2.19 Algorithm Version Number Query

**Method:** `GET` | **URL:** `http://Device IP:8090/getSDKVersion`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| type | Algorithm type | Int | N | Algorithm type:\|1.Face SDK (by default)\|2.Fingerprint SDK

**Response Format:**


### 2.20 Device Information Query

**Method:** `GET` | **URL:** `http://Device IP:8090/device/information`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Device password

**Response Format:**


### 2.21 Signal Input Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/device/ setSignalInput`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Device password
| config | Configuration collection of hardware Interfaces | Json | Y | Example of Json:\|{\|"inputNo":1,\|"type":1,\|"Name":"Fire alarm"\|}
| inputNo | Int | Y | Signal serial number\|1: Signal input 1, the label on the wire is Alarm1 (old wire) /Button (new wire) (Default: Exit button)\|2: Signal input 2, the label on the wire is Alarm2 (old wire) /Sensor (new wire) (Default: Door sensor) | 
| type | Int | Y | 1: Fire alarm input (Signal 2 default) \|2: Door sensor input\|3: Exit button input (Signal 1 default)\|Only supported by overseas devices | 
| name | String | N | Signal name\|It can be customized\|The length is limited to 32 characters | 

**Response Format:**


### 2.22 Signal Input Setting Query

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getSignalInput`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Device password

**Response Format:**


### 2.23 Alarm Cancellation

**Method:** `POST` | **URL:** `http://Device IP:8090/device/alarmCancel`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Response Format:**


### 2.24 Temperature Measurement Parameter Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setTemperatureConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| isTemperatureOpen | Whether to enable the temperature measurement mode | Int | Y | 1: On (by default)  \|2: Off  \|After enabling the temperature measurement mode, b
| errorTemperature | Judgement value of abnormal temperature | String | Y | Judgement value of abnormal temperature, default value is 37.3℃, temperature hig
| temperatureErrorPass | Abnormal body temperature access switch | Int | N | 1: On \|2: Off (by default)
| temperatureMeasureMin | Mininum value of effective temperature | String | N | The temperature lower than this value will not be recorded, and the user will be
| temperatureMeasureMax | Maximum value of effective temperature | String | N | The temperature higher than this value will not be recorded, and the user will b
| fastPass | Fast pass | Int | N | 1: On\|2: Off

**Response Format:**


### 2.25 Mask Parameter Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setMaskConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| maskDetect | Mask detection parameters | Int | Y | 1: General tips\|2: Off\|3: Mandatory wearing\|4: Compulsory non-wearing of masks (
| isVoiceOpen | Mask voice prompt switch | int | Y | 1: On (default)\|2: Off

**Response Format:**


### 2.26 Mask Parameter Query

**Method:** `GET` | **URL:** `http://Device IP:8090/getMaskConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 

**Response Format:**


### 2.27 Event Call-back

**Method:** `POST` | **URL:** `http://Device IP:8090/device/eventCallBack`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Call-back address | String | Y | Send POST fields to the address as alarm occurs, refer to Callback field specifi
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Millisecond timestamp of device current time | "time":"1537236693823" | 
| ip | String | Current device IP address | "ip":"192.168.20.66" | 
| event | json | Collection of events | Example of Json:\|{\|"eventType":1,\|"signalSource":1\|} | 
| eventType | Type of event | Int | 1. Fire alarm\|2. Door sensor opened\|3. Door sensor closed\|4. Tamper alarm\|5. Recognition event\|7. Password decode\|8. Stress alarm\|100.Self-defined types Supported by overseas devices only | 
| signalSource | Source of input signal | Int | When event type is fire alarm, door sensor or exit button, this parameter will appear\|Signal input 1\|Signal input 2\|Anti-tamper button (Below the back connector) | 
| Specific fields of recognition event | Specific fields of recognition event | Specific fields of recognition event | Specific fields of recognition event | 
| personId | PersonID | String | Recognize ID of corresponding person | 
| idcardNum | Card number of the person | String | Card number of the person | 
| result | Recognition result | Int | Recognition result\|1. Recognition succeeded\|2. Recognition failed\|3. Permission denied | 
| data | ID info of the person | String | ID card info of the person | 
| Unique fields after the temperature measurement switch is turned on | Unique fields after the temperature measurement switch is turned on | Unique fields after the temperature measurement switch is turned on | Unique fields after the temperature measurement switch is turned on | 
| errorTemperature | Abnormal body temperature judgment value | String | The unit of "37.3" is subject to the device configuration, and upload Celsius or Fahrenheit | 
| temperature | Body temperature during scanning | String | When the "xx.x" temperature measurement switch is not turned on, pass in null value. When the temperature measurement switch is turned on, if temperature not measured and measurement timed out, pass in "0.0". If the temperature is illegal, pass in "-100.0". The unit is subject to the device configuration, and upload Celsius or Fahrenheit | 
| password decode event specific fields | password decode event specific fields | password decode event specific fields | password decode event specific fields | 
| unlockTime | User locked time | Int | Locked time, unit s | 
| userName | User name | string | "admin" | 
| ttsModContent | String | Custom voice output | No more than 64 bits, no more than 10 bits. The default is null | 
| displayModContent | String | Interface display content | No more than 64 bits, no more than 10 bits. The default is null | 
| isOpenRelay | Int | Whether to open the door by relay | 1 means on, others not | 

**Response Format:**


### 2.28 QR Code Call-back

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setQRCodeCallback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Callback url | String | Y | Passing in null content can clear callback address, then the device will not do 
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Millisecond timestamp of current time | "time":"1537236693823" | 
| ip | String | Current IP address | "ip":"192.168.20.66" | 
| QRdata | String | QR code info | "QRdata":"123456" | 

**Response Format:**


### 2.29 Anti-flicker Switch Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setAntiStroboscopicSwitch`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| AntiStroboscopicSwitch | Anti-flicker switch | Int | Y | 

**Notes:** Note: Only 6CC devices are supported. Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Set successfully", "result": 1, "success": true }

**Response Format:**


### 2.30 Registration Information Callback Address

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setRegistCallback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Callback address | String | Y | If the incoming content is empty, the callback address can be cleared. After cle
| type | Type | Int | Y | Photo\|Card number\|Fingerprint\|QR code\|Person info Supported by overseas devices 
| base64Enable | On-site photo base64 switch | int | N | Off (by default) \|On (Only enable when type is 1)

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "http://192.168.16.250:8888/lan/QRCodeCallback", "msg": "Set successfully", "result": 1, "success": true }

**Response Format:**


### 2.31 Language Switch (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setLanguage`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Password | String | Y | 
| languageType | Type of language | String | Y | Type of language:\|"zh_CN": Simplified Chinese\|"en": English

**Response Format:**


### 2.32 Timezone Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setTimeZone`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| timeZone | Language type | String | Y | "GMT+5"\|See Exhibit 2 for other time zones\|Inquiries can be made at Equipment In

**Response Format:**


### 2.33 Summer Timezone Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/ setSummerTimeZone`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Device password
| isEnable | Timezone | Bool | Y | true: enable summer timezone setting\|false: disable summer timezone setting
| startDate | Starting time | String | Y | Daylight Saving Time opening date\|For example, 1.10
| endDate | ending time | String | Y | Daylight Saving Time end date\|For example, 12.20

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "set up successfully", "result": 1, "success": true }

**Response Format:**


### 2.34 Attendance Status Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setAttendanceStatus`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| config | Collection of personnel information | Array | Y | Example of Json:\|[{"id":1,"status":"On Work"},{"id":2,"status":"Off Work"},{"id"
| method | Attendance mode | Int | Y | 1 Manual, 2 Automatic\|(Note: Method parameter must be passed when enable: 2; oth
| enable | Switch | Int | Y | Attendance mode switch, 1 Off, 2 On
| id | Attendance status value | Int | N | Attendance status value\| Note: If this attribute is filled in, the status attrib
| status | Attendance status description | String | N | String description information
| period | Automatic attendance cycle | String | N | For example: "12:00:00, 13:00:00, 18:00:00, 19:00:00", up to 12 time points (6 g
| color | Attendance Status Color | Int | N | Only 9 colors are supported (fill in the number corresponding to the color)\|1 Gr

**Notes:** Request data Header domain Body domain Note: when enable is set to 2, the mutually exclusive mechanism of attendance status and work code will be detected after the attendance status is enabled Config parameter Note: The number of arrays in config is at least 0 and at most 6 Only the following two config formats are valid. Invalid config formats will be ignored and will not be saved { "id": 1, "st

**Response Format:**


### 2.35 Attendance Status Query (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/getAttendanceStatus`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Response Format:**


### 2.36 Workcode Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setWorkcode`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| workcodes | Workcode collection | Array | Y | [{"name":"Boatman", "id":"111"},{"name":"Carpenter", "id":"222"},{"name":"Sailor
| enable | Switch | Int | Y | Work code enable switch, 1 Off, 2 On
| id | Workcode | Int | Y | Work code (Only numbers and English letters are allowed)
| name | Workcode name | String | Y | Workcode name

**Notes:** Request data Header domain Body domain Note: When enable is set to 2 and the work code is enabled, the attendance status and the mutually exclusive mechanism of the work code will be detected Workcode parameter Note: The number of arrays in workcodes is at least 0 and at most 8; Postman example Return example { "code": "LAN_SUS-0", "msg": "set successfully", "result": 1, "success": true }

**Response Format:**


### 2.37 Workcode Query (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/getWorkcode`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "enable": 2, "workcodes": [ { "id": "111", "name": "11111" }, { "id": "222", "name": "Carpenter" }, { "id": "333", "name": "Sailor" }, { "id": "444", "name": "Porter" }, { "id": "555", "name": "Director" }, { "id": "666", "name": "Manager" }, { "id": "777", "name": "Employee" }, { "id": "888", "n

**Response Format:**


### 2.38 Schedule Creation (Only supported by overseas devices)(Reserved interface only)

**Method:** `POST` | **URL:** `http://Device IP:8090/ schedule/create`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| scheduleld | Schedule id | Int | Y | Unique ID, not repeatable\|Starts at 1000, less than 1000 is an internal reserved
| scheduleType | Schedule type | Int | Y | 0: Daily schedule\|1: Weekly schedule\|2: Holiday schedule
| scheduleName | Schedule name | String | N | Not filled in, default as the same id
| schedulePasstime | Allowed passtime | String | N | The range is [00:00:00, 23:59:59], subject to the device time\|Daily and holiday 
| validTime | Schedule validity | String | N | The passed-in time format is (year-month-day hour:minute:second)\|The start and e

**Response Format:**


### 2.39 Schedule Deletion (Only supported by overseas devices)(Reserved interface only)

**Method:** `POST` | **URL:** `http://Device IP:8090/schedule/delete`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| scheduleId | Schedule id | Int | Y | Multiple can be passed in, separated by commas.\|The schedule being associated wi

**Response Format:**


### 2.40 Schedule Update (Only supported by overseas devices)(Reserved interface only)

**Method:** `POST` | **URL:** `http://Device IP:8090/ schedule/update`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| scheduleld | Schedule id | Int | Y | Unique ID, not repeatable
| scheduleName | Schedule name | Int | N | Not filled in, default as the same id
| scheduleType | Schedule type | Int | Y | 0: Daily schedule\|1: Weekly schedule\|2: Holiday schedule
| schedulePasstime | Allowed passtime | String | N | The range is [00:00:00, 23:59:59], subject to the device time\|Daily and holiday 
| validTime | Schedule validity | String | N | The passed-in time format is (year-month-day hour:minute:second)\|The start and e

**Response Format:**


### 2.41 Schedule Query (Only supported by overseas devices)(Reserved interface only)

**Method:** `POST` | **URL:** `http://Device IP:8090/schedule/find`

**Response Format:**


### 2.42 Anti-passback Parameter Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/ device/SetAntiPassback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | application/x-www-form-urlencoded | 
| pass | Device password | String | Y | 
| config | Anti-passback parameter config | Json | Y | {\|"antiPassbackEnable":2,\|"io232":1,\|"io485":2,\|"ioWiegand":2,\|"ioUsb":2,\|"ioLoc
| antiPassbackMode | Anti-passback switch | Int | N | 1: Off\|2: local ASW\|3: Linkage Anti-passback\|Note:3 can only be set via the plat
| antiPassbackType | Anti-passback type | Int | N | 1: out of anti-passback\|2: Into anti-passback.\|3: in and out of anti-passback
| io232 | External 232 input | Int | N | 0: Not marked,\|\|\|(232 card swiping)
| io485 | External 485 input | Int | N | 0: Not marked,\|\|\|(485 card swiping)
| ioUsb | External USB input | Int | N | 0: Not marked,\|\|\|(USB card reader, QR code reader, etc.)
| ioWiegand | External Wiegand input | Int | N | 0: Not marked,\|\|\|(Wiegand card board)
| ioLocalModule | Local recognition module | Int | N | 0: Not marked,\|\|\|(Camera, TTL card board, touch screen)

**Response Format:**


### 2.43 Anti-passback Parameter Query (Only supported by overseas devices)

**Method:** `GET` | **URL:** `http://device IP:8090/device/getAntiPassback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 

**Response Format:**


### 2.44 Anti-passback Status Clearing (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://decice IP:8090/device/clearAntiPassbackStatus`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 

**Response Format:**


### 2.45 Get on-site personnel (Only supported by overseas devices)

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getInternalStaff`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| length | Quantity of the maximum number per page | int | N | The incoming value of length is required to be a positive integer between (0, 10
| order | sort by | int | N | If the order is not passed, the default is to sort by time in descending order
| index | page number | int | Y | Page number starts from 0


### 2.46 Screensaver Image Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setScreenImg`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| imgBase64 | Screensaver image | Int | Y | Without the header, for example: data: image/jpg; base64,\|Passing in -1 means to

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Image set successfully", "result": 1, "success": true "timestamp": 1618913373248 }

**Response Format:**


### 2.47 Health Code Parameter Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/setHealthCodeParams`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| isHealthCodeOpen | Epidemic prevention detection switch | Int | N | 1: On (by default)\|2: Off
| idCardType | ID card verification switch | Int | N | 1: On\|2: Off
| healthCodeNetErrorOpen | Network abnormality access switch | Int | N | 1: On\|2: Off (by default)
| serviceType | Source of health code | Int | N | 1: wo\|2: Callback
| showSecond | Health code display duration | Int | N | Default 3s (1~10s)
| alarmSecond | Health code abnormality alarm duration | Int | N | Default 10s (1~99s)
| vistorPassSwitch | Visitors are allowed to pass | Int | N | 1: On\|2: Off
| travelCheckSwitch | Restriction access switches in medium and high risk areas | Int | N | 1: On\|2: Access is allowed without digital travel record\|3: Off
| vaccinateCheckSwitch | Vaccine verification | Int | N | 1: Restrict access by the number of vaccinations
| vaccinateCheckTimes | Number of vaccinations | Int | N | Number of vaccinations (0~5)
| nucleicCheckSwitch | Nucleic acid detection switch | Int | N | On\|Off
| nucleicCheckValidtime | Validity of nucleic acid | Int | N | Unit: default as hour\|Note: must be used in pairs with nucleicccheckvalidunit
| nucleicCheckValidUnit | Nucleic acid validity unit | Int | N | Hour (1~100)\|Day (1~180)\|Note: must be used in pairs with nucleicCheckValidtime
| httpEventUrl | Event callback address | String | N | 
| httpQRCodeUrl | Code scanning callback address | String | N | 
| httpTimeout | Timeout of the third-party callback platform interface | Int | N | Unit: second (1~30)
| woTimeout | SaaS timeout | Int | N | Unit: second (1~30)

**Notes:** Attention: Only supported by mask thermometry devices Request data Header domain Body domain Postman example


### 2.48 Person Update Call Back Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/setPersonUpdateCallBack`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| url | Call-back address | string | Y | 
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Device current time millisecond timestamp | "time":"1537236693823" | 
| ip | String | Device current IP address | "ip":"192.168.20.66" | 
| id | String | Personnel id | "id":"001" | 
| name | String | Personnel name | "name":"001abc" | 
| idcardNum | String | Personnel card number | "idcardNum":"089788712" | 
| facePermission | String | Face Recognition Permission | "facePermission":"" | 
| idCardPermission | String | Card Recognition Permission | "idCardPermission":"1" | 
| passwordPermission | String | Password Recognition | "passwordPermission":"1" | 
| fingerPermission | String | Fingerprint Recognition | "fingerPermission":"1" | 
| qrCodePermission | String | QRcode Recognition | "qrCodePermission":"1" | 
| faceAndCardPermission | String | Human Card Combination Permission | "faceAndCardPermission":"1" | 
| cardAndPasswordPermission | String | Card+Password Permission | "cardAndPasswordPermission":"1" | 
| faceAndQrCodePermission | String | Face + QR Code | "faceAndQrCodePermission":"1" | 
| qrCode | String | Personnel QR Code | "qrCode":"qrCodeUrl" | 
| password | String | Password | "password":"123456" | 
| tag | String | Personnel Remarks | "tag":"001abc" | 
| role | String | Personnel Role | "role":"0" \|0: permanent, 1: temporary persons | 
| scheduleId | String | Bound schedule id | "scheduleId":"7" | 
| uploadCMD | String | Person update type | "uploadCMD":1\|1 New\|2 Update\|3 Delete | 
| faceAndFingerPermission | String | Face + Fingerprint Permission | "faceAndFingerPermission":"1" | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "http://192.168.41.41:8888/api/PersonUpdateCallback", "msg": "set up successfully", "result": 1, "success": true } Description of Person Update Callback Parameter Fields

**Response Format:**


### 2.49 Set personnel update callback to reissue (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setOfflinePersonUpdate`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| offlineDataUploadEnable | Offline data upload mechanism switch | int | N | Off by default, keeps the last setting if empty,\|\|\|If the callback data upload f
| pageLimit | The maximum amount of data in a single data package | int | N | 1~100 Only effective when package switch packEnable is on, 10 by default
| packEnable | Offline data upload package switch | int | N | Off by default, keeps the last setting if empty,\|\|\|When the callback data is rei

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "set up successfully", "result": 1, "success": true }

**Response Format:**


### 2.50 Get personnel update callback reissue configuration (Only supported by overseas devices)

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getOfflinePersonUpdate`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "offlineDataUploadEnable": 1, "packEnable": 1, "pageLimit": 10 }, "msg": "search successful", "result": 1, "success": true }

**Response Format:**


### 2.51 Printer Config Setting (Only supported by overseas devices)

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setPrinterConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| config | Print information collection | Json | Y | {\|"content1": "There's two",\|"content2": "And then there's four",\|"content3": "A
| content1 | Custom row 1 | string | N | Custom text content from top to bottom in row 1
| content2 | Custom row 2 | string | N | Custom text content from top to bottom in row 2
| content3 | Custom row 3 | string | N | Custom text content from top to bottom in row 3
| content4 | Custom row 4 | string | N | Custom text content from top to bottom in row 4
| content5 | Custom row 5 | string | N | Custom text content from top to bottom in row 5
| content6 | Custom row 6 | string | N | Custom text content from top to bottom in row 6
| printerEnable | Printer switch | int | Y | 1. Off (by default) 2. On

**Notes:** Request data Header domain Body domain Config setting Postman example Return example { "code": "LAN_SUS-0", "msg": "set up successfully", "result": 1, "success": true }

**Response Format:**


### 2.52 Get printer configuration (Only supported by overseas devices)

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getPrinterConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "content2": "qwertyuiopqwertyuiopqwertyuiopqwertyuiop", "content3": "012345678901234567890123456789012345678901234567890123456789", "content4": "!@#$%^&*()_+!@#$%^&*()_+!@#$%^&*()_+!@#$%^&*()_+!@#$%^&*()_+!@#$%^&*()_+", "content5": "We're done.", "content6": "Good Morning", "printerEnable": 2 }, 

**Response Format:**


### 2.53 Fingerprint Enrollment Callback Settings

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setFingerRegCallback`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| url | Call-back address | String | Y | After the fingerprint registration is successful (including the device recording
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Device time (millisecond timestamp) when photo registration was successful | "time":"1537236693823" | 
| ip | String | Device current IP address | "ip":"192.168.20.66" | 
| personId | String | Fingerprint registration corresponding to the person id | "personId":"abcd" | 
| feature | String | Fingerprint eigenvalue |  | 
| featureKey | String | Feature secret key, this field is required for feature validity verification when registering by feature code |  | 
| faceId | String | Fingerprint id |  | 
| SDKVersion | String | Device Algorithm Version |  | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "http://192.168.79.47:1111/FingerRegCallback", "msg": "Setting success", "result": 1, "success": true } Description of Fingerprint Enrollment Callback Parameter Fields Requirements: callback data in the url and body each have a copy, the data in the url is key-value pairs, the data in the body is a

**Response Format:**


### 2.54 Signal Output Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/device/getSignalOut`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | 
| config | Device Hardware Interface Configuration Collection | Json | Y | Json example:\|{\|" outputNo":1,\|"type":1\|}
| outputNo | Int | Y | Signal number\|1:Signal output 1, currently only one way signal 1 | 
| type | Int | Y | 0: no output (signal 1 default)\|1: anti-tamper alarm output signal\|2: Fire alarm output signal\|3: Doorbell output signal\|only supported by U02 devices | 

**Notes:** Request data Header domain Body domain Config parameter description http request example Return example { "code": "LAN_SUS-0", "data": [ { "type": 1 } ], "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.55 Signal Output Setting Query

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getSignalOut`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "data": [ { "type": 1 } ], "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.56 Write Secret Key

**Method:** `POST` | **URL:** `http://Device IP:8090/device/writeSecretKey`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| writeSecretKey | Secret key | String | Y | Secret key

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.57 Read Secret Key

**Method:** `GET` | **URL:** `http://Device IP:8090/device/readSecretKey`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "data": "hahahah", "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.58 Set Card Management Configuration

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setCardManagerConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| config | Card Management Configuration | Object | Y | Card Management Configuration\|{\|	"addCard": "456",\|	"deleteCard": "789",\|	"regis
| addCard | Add Card | String | N | Add person card, can pass empty string
| deleteCard | Delete Card\|Registration Type | String | N | Delete person card, can pass empty string
| registerType | Registration Type | Int | N | 1: Register with face\|2: Register with card

**Notes:** Request data Header domain Body domain Config parameter description http request example Return example { "code": "LAN_SUS-0", "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.59 Get Card Management Configuration

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getCardManagerConfig`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "data": { "addCard": "456", "deleteCard": "789", "registerType": 1 }, "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.60 Quick registration of add or delete cards

**Method:** `POST` | **URL:** `http://Device IP:8090/device/quickCardRegister`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| type | Card Type | Int | Y | Card Type\|1: Card for adding person\|2: Card for deleting person

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "msg": "Please place the card in the card reader area", "result": 1, "success": true }

**Response Format:**


### 2.61 Set dynamic screen saver image

**Method:** `POST` | **URL:** `http://Device IP:8090/device/device/setGif`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| gif | Dynamic image information | Object | Y | Dynamic image information
| operator | Operation type | int | Y | 1:Replace the dynamic screen saver image\|2:Restore default screen saver image
| base64 | Dynamic image base64 content | String | When type is 1, it must pass | Dynamic image base64 content

**Notes:** Request data Header domain Body domain gif parameter description http request example Return example { "code": "LAN_SUS-0", "data": { "filename": "31fbf3d4c8" }, "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.62 Add static rotating image

**Method:** `POST` | **URL:** `http://Device IP:8090/device/addStaticPic`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| base64 | Image base64 | String | Y | Image base64

**Notes:** Request data Header domain Body domain http request example Return example { "code": "LAN_SUS-0", "data": { "filename": "be1713d881" }, "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.63 Delete static rotating image

**Method:** `DELETE` | **URL:** `http://Device IP:8090/device/delStaticPic`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| filename | Image files to be deleted | String | Y | Image files to be deleted\|Pass "-1" to delete all static images\|Support batch de

**Notes:** Request data Header domain Body domain http request example Return example { "code": "LAN_SUS-0", "data": { "delFile": [ "be1713d881" ] }, "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.64 Get custom screensaver configuration

**Method:** `GET` | **URL:** `http://Device IP:8090/device/getScreenSaver`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password

**Notes:** Request data Header domain Query domain http request example Return example { "code": "LAN_SUS-0", "data": { "screenSaver": { "enable": true, "gif": [ { "checked": true, "filename": "31fbf3d4c8" } ], "image": [ { "checked": true, "filename": "767b59623d" } ], "span": 1, "type": 1 } }, "msg": "Operation succeeded", "result": 1, "success": true }

**Response Format:**


### 2.65 Set custom screensaver configuration

**Method:** `POST` | **URL:** `http://Device IP:8090/device/setScreenSaver`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | string | Y | application/x-www-form-urlencoded
| pass | Device password | string | Y | Device password
| screenSaver | Custom screen saver configurations | Object | Y | Custom screen saver configurations
| enable | Custom Screensaver Enable | bool | N | Custom Screensaver Enable
| gif | Dynamic image information | Object[] | N | Currently supports up to 1 custom dynamic screensaver image
| +checked | whether to select the Dynamic Image | bool | Y | whether to select the Dynamic Image
| +filename | File name | String | Y | File name
| image | Static rotating image information | Object[] | N | Static rotating image information
| +checked | Whether to select static image | bool | Y | Whether to select static image
| +filename | File name | String | Y | File name
| span | Rotation interval | Int | N | Rotation interval 1~30 seconds
| type | Customised screensaver image type | Int | N | 1:Static image\|2:Dynamic image

**Notes:** Request data Header domain Query domain screenSaver parameter description http request example Return example { "code": "LAN_SUS-0", "data": { "screenSaver": { "enable": true, "gif": [ { "checked": true, "filename": "31fbf3d4c8" } ], "image": [ { "checked": true, "filename": "767b59623d" } ], "span": 1, "type": 1 } }, "msg": "Operation succeeded", "result": 1, "success": true } Human Resource Mana

**Response Format:**


## III. Personnel Management


### 3.1 Personnel Registration

**Method:** `POST` | **URL:** `http://Device IP:8090/person/create`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| person | Collection of personnel information | Json | Y | Example of Json:\|{\|"id":"001",\|"name":"",\|"idcardNum":"",\|"facePermission":2,\|"i
| face1 | Registration photo 1 information | Json | N | {\|"faceId":"001",\|"url":"url",\|"base64":"base64",\|"isEasyWay":"false",\|"bbox":{"
| face2 | Registration photo 2 information | Json | N | Same as face1\| Support overseas devices only
| face3 | Registration photo 3 information | Json | N | Same as face1\| Support overseas devices only
| id | Person Id | String | N | Can pass in null content. Content allows numbers and English letters only, case 
| name | Person name | String | Y | Name parameter must be passed and its content cannot be empty.\|The length is lim
| idcardNum | Card number | String | N | Can be null when registering,the length is limited to 32 characters,only numbers
| iDNumber | ID number | String | N | Can leave it blank when registering, fill in the correct ID card\|Note: this fiel
| facePermission | Single verification method\|Face recognition permission | Int | N | 1: Off \|2: On (by default)\|Single authentication method can be multi-selected an
| idCardPermission | Single verification method\|Card recognition permission | Int | N | 1: Off \|2: On (by default)
| iDNumberPermission | Single verification method\|ID card recognition permission | Int | N | 1: Off \|2: On (by default)
| passwordPermission | Single verification method\|Password verification permission | Int | N | 1: Off (by default) \|2: On
| fingerPermission | Single verification method\|Fingerprint verification permission | Int | N | 1: Off (by default) \|2: On
| qrCodePermission | QR code comparison | Int | N | Switch of QR code permission\|1: Off (by default)\|2: On\|Only supported by oversea
| faceAndCardPermission | Compound verification method\|Face & Card Verification | Int | N | 1: Off (by default)\|2: On\|Can coexist with a single authentication method (excep
| cardAndPasswordPermission | Card & Password verification permission | Int | N | 1: Off (by default)\|2: On\|Mutually exclusive with single verification method\|Onl
| faceAndQrCodePermission | Face + QR code door opening permission | Int | N | 1: Off (by default)\|2: On\|Mutually exclusive with single authentication method\|O
| faceAndFingerPermission | Face + Fingerprint door opening permission | Int | N | 1: Off (by default)\|2: On\|Mutually exclusive with single authentication method\|O
| faceAndPasswordPermission | Face + Password door opening permission | Int | N | 1: Off (by default)\|2: On\|Mutually exclusive with single authentication method
| fingerAndPasswordPermission | Fingerprint + Password door opening permission | Int | N | 1: Off (by default)\|2: On\|Mutually exclusive with single authentication method
| tag | Personnel remarks | String | N | It can be left blank when registering, the length is limited to 60 characters, a
| qrCode | QR code content | String | N | Content contained in QR code\|Only supported by overseas devices
| password | User password | String | N | It can be left blank when registering, but if it is, it cannot be a null value.L
| role | Personnel type | Int | N | 0: Regular personnel (by default). After the expiration of the personnel validit
| scheduleId | Associated schedule | String | N | Associated schedule id\|Multiple can be passed in, separated by commas\|Only suppo
| phone | Phone Number | String | N | Registration can be left blank, the content only allows numbers, the length limi
| rule | Person association rule information | Object[] | N | 
| +timezoneRule | Time Rule | Object | N | Time rule
| ++ruleId | Rule id | String | N | Rule id

**Notes:** Request data Header domain Body domain Person parameter Note: parameters without ☆ symbol are unique parameters of Hisilicon devices, which are not available in Android devices. Face example Only supported by overseas devices Postman example Return example Attention: Name and card number registered successfully, meaning to write in personnel information into the device database. If using device to

**Response Format:**


### 3.2 Personnel Deletion (in batch)

**Method:** `POST` | **URL:** `http://Device IP:8090/person/delete`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 
| id | Person ID | String | Y | If deleting multiple personnel, joins their id with English commas \|Pass in -1 t

**Notes:** Request data Body domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "msg": "Database is cleared, related image files have been deleted", "result": 1, "success": true } Example 2 of return: pass in multiple people for personId { "code": "LAN_SUS-0", "data": { "effective": "128", "invalid": "" }, "msg": "The content in effective represents a valid ID that has

**Response Format:**


### 3.3 Personnel Update

**Method:** `POST` | **URL:** `http://Device IP:8090/person/update`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| person | Collection of personnel information | Json | Y | {\|"id":"001",\|"name":"",\|"idcardNum":"",\|"iDNumber":"",\|"facePermission":2,\|"idC
| face1 | Registration photo 1 information | Json | N | {\|"faceId":"001",\|"url":"url",\|"base64":"base64",\|"isEasyWay":"false",\|"bbox":{"
| face2 | Registration photo 2 information | Json | N | Same as face1\| Support overseas devices only
| Face3 | Registration photo 3 information | Json | N | Same as face1\| Support overseas devices only
| id | Person Id | String | Y | id of target person is required.
| name | Name | String | Y | name parameter is required and content cannot be null. The length is limited to 
| idcardNum | Card number | String | N | If passing in null, then update is null, if not passing in, use the previous val
| iDNumber | ID number | String | N | If passing in null or not passing in, use the previous value.\|Note: this field i
| facePermission | Single verification method\|Face recognition permission | Int | N | 1: Off \|2: On (by default)\|Single authentication methods can be multi-selected a
| idCardPermission | Single verification method\|Card recognition permission | Int | N | 1: Off \|2: On (by default)
| passwordPermission | Single verification method\|Password verification | Int | N | 1: Off (by default) \|2: On
| fingerPermission | Single verification method\|Fingerprint verification | Int | N | 1: Off (by default) \|2: On
| iDNumberPermission | Single verification method\|ID card verification | Int | N | 1: Off (by default) \|2: On
| qrCodePermission | QR code comparison | Int | N | QR code permission switch\|1. Off (by default)\|2. On\|Only supported by overseas d
| faceAndCardPermission | Compound verification method\|Face&Card verification | Int | N | 1: Off (by default) \|2: On\|Can coexist with a single authentication method (exce
| cardAndPasswordPermission | Card + Password verification permission | Int | N | 1: Off (by default) \|2: On\|Mutually exclusive with single verification method\|On
| faceAndQrCodePermission | Face+QR code verification permission | Int | N | 1: Off (by default) \|2: On\|Mutually exclusive with single verification method\|On
| faceAndFingerPermission | Face+Fingerprint verification permission | Int | N | 1: Off (by default)\| 2: On\|Mutually exclusive with single verification method\|On
| faceAndPasswordPermission | Face+Password verification permission | Int | N | 1: Off (by default)\| 2: On\|Mutually exclusive with single verification method
| fingerAndPasswordPermission | Fingerprint+Password verification permission | Int | N | 1: Off (by default)\| 2: On\|Mutually exclusive with single verification method
| tag | Remarks (users can custom) | String | N | If passing in null, then update is null, if not passing in, use the previous val
| qrCode | QR code content | String | N | Content contained in QR code\|Only supported by overseas devices
| password | User password | String | N | Length 6 bits, only numbers are allowed, and symmetric passwords are not allowed
| role | Personnel type | Int | N | 0: Regular personnel (by default). After the expiration of the personnel validit
| scheduleId | Associated schedule | String | N | Associated schedule id\|Multiple can be passed in, separated by commas\|only suppo
| phone | Phone number | String | N | Pass null to update to null, do not pass to use the last value, the content is o
| rule | Person association rule information | Object[] | N | 
| +timezoneRule | Time Rule | Object | N | Time rule
| ++ruleId | Rule id | String | N | Rule id

**Notes:** Request data Header domain Body domain Person parameters Face example Only supported by overseas devices Postman example Return example { "code": "LAN_SUS-0", "data": { "cardAndPasswordPermission": 1, "createTime": 1655963846392, "faceAndCardPermission": 1, "faceAndQrCodePermission": 1, "facePermission": 2, "iDNumber": "", "id": "433", "idCardPermission": 2, "idcardNum": "3806111558", "name": "Out

**Response Format:**


### 3.4 Personnel Query

**Method:** `GET` | **URL:** `http://Device IP:8090/person/find`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 
| id | Person ID | String | Y | Query person information of designated id\|Passing in -1 for id to query all pers

**Notes:** Request data Query domain Postman example Explanation for different conditions Attention: when using postman, parameter of GET request is put in url, tap "Params" to add parameters. Condition 1: pass in id of designated person for personId. Return example { "code": "LAN_SUS-0", "data": [ { "cardAndPasswordPermission": 1, "createTime": 1655963846392, "faceAndCardPermission": 1, "faceAndQrCodePermis

**Response Format:**


### 3.5 Personnel Query in Page

**Method:** `GET` | **URL:** `http://Device IP:8090/person/findByPage`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Query person information of designated id \|passing in -1 for id means not limite
| length | Max. number in each page | Int | N | Passed-in value of length requires positive Integers between (0,1000]\|If not pas
| index | Page | Int | N | Page starts from 0. Passed-in value of index must be less than total pages, for 

**Notes:** Request data Query domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "data": { "pageInfo": { "index": 0, "length": 10, "size": 1, "total": 2 }, "personInfos": [ { "cardAndPasswordPermission": 1, "createTime": 1655435452374, "faceAndCardPermission": 1, "faceAndQrCodePermission": 1, "facePermission": 2, "iDNumber": "", "id": "233", "idCardPermission": 1, "idc

**Response Format:**


### 3.6 Card Number Registration

**Method:** `POST` | **URL:** `http://Device IP:8090/face/icCardRegist`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Register card number for designated person ID\|Person ID must exist; if ID not ex

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "IC card registration mode is enabling, enrolled card number can be queried according to personId after successful registration. Please complete the registration with guidance", "result": 1, "success": true }

**Response Format:**


### 3.7 Personnel Fingerprint Registration

**Method:** `POST` | **URL:** `http://Device IP:8090/face/fingerRegist`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Personnel ID | String | Y | Register fingerprint for designated person Id\|The person Id must already exist; 

**Notes:** Request data Header domain Body domain Return example { "code": "LAN_SUS-0", "msg":"Fingerprint registration mode is enabling. Please follow the instructions to complete the registration", "result": 1, "success": true }

**Response Format:**


### 3.8 Passtime Permission Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/person/createPasstime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| passtime | Allowed passtime for some person everyday | String | Y | Example of Json:\|{"personId":"9eecc839cd7941c5a4d3165202dd3c32","passtime":"09:0

**Notes:** Note: If the overseas device has both time period authority and time rule set up, the pass time is based on the time period authority Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "passtime set successfully", "result": 1, "success": true }

**Response Format:**


### 3.9 Passtime Permission Setting in Batch

**Method:** `PUT` | **URL:** `http://Device IP:8090/person/passtime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| passtime | Allowed passtime of some person everyday | String | Y | Example of Json:\|{"passtime":"09:00:00,10:00:00,17:00:00,17:30:00,18:30:00,20:25
| personId | Person Id | String | Y | If setting the passtime for multi-personnel, personId is joined by English comma

**Notes:** Note: Note: If the overseas device has both time period authority and time rule set up, the pass time is based on the time period authority Request data Header domain Body domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "msg": "passtime of all personnel set successfully", "result": 1, "success": true } Example 2 of return: pass in personId for multiple pe

**Response Format:**


### 3.10 Passtime Permission Deletion in Batch

**Method:** `POST` | **URL:** `http://Device IP:8090/person/deletePasstime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person Id | String | Y | Delete the passtime permission settings for this person, this person will no lon

**Notes:** Note: Note: If the overseas device has both time period authority and time rule set up, the pass time is based on the time period authority Request data Header domain Body domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "msg": " passtime of all personnel deleted successfully", "result": 1, "success": true } Example 2 of return: pass in personId ofr multip

**Response Format:**


### 3.11 Expiry Date Setting

**Method:** `POST` | **URL:** `http://Device IP:8090/person/permissionsCreate`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| time | Time of expiry date, delete this person on time | String | Y | Subject to device system time, when person permission is expired, this person wi
| personId | Person Id | String | Y | Support single person only

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "permissionTime set successfully", "result": 1, "success": true }

**Response Format:**


### 3.12 Expiry Date Setting in Batch

**Method:** `PUT` | **URL:** `http://Device IP:8090/person/permissionTime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person Id | String | Y | If setting passtime for multiple personnel, joins personId with English commas\|I
| startTime | Start time | String | Y | Format of pass-in time is (Year-Month-Day Hour:Minute-Second): 2017-07-15 12:05:
| endTime | End time | String | Y | Format of pass-in time is (Year-Month-Day Hour:Minute-Second): 2017-07-15 12:05:

**Notes:** Request data Header domain Body domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "msg": "permissionTime of all personnel set successfully", "result": 1, "success": true } Example 2 of return: pass in multiple personnel for personId { "code": "LAN_SUS-0", "data": { "effective": "df6242d810674d42b79acf6b94106048", "invalid": "123" }, "msg": "Content in "effe

**Response Format:**


### 3.13 Expiry Date Deletion in Batch

**Method:** `POST` | **URL:** `http://Device IP:8090/person/permissionsDelete`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person Id | String | Y | To delete permission time of multiple personnel, joins personId with English com

**Notes:** Request data Header domain Body domain Postman example Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "msg": "permissionTime of all personnel deleted successfully", "result": 1, "success": true } Example 2 of return: pass in multiple personnel for personId { "code": "LAN_SUS-0", "data": { "effective": "004", "invalid": "73d0ecee1c5e4ce89d1ece7b082b203d,1130" }, "msg": "Content

**Response Format:**


### 3.14 Personnel Permission Query

**Method:** `GET` | **URL:** `http://Device IP:8090/person/permissionInfo`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person Id | String | Y | Query person info of designated id \|Pass in -1 for id, meaning personnel query n
| length | Max. numbers in each page | Int | N | Incoming value of length requires positive Integer between (0,1000],\|If not pass
| index | Page | Int | N | Page starts from 0, incoming value of index must be smaller than total number of

**Notes:** Request data Header domain Body domain Postman example Note: some of the attributes ( cardAndPasswordPermission / faceAndQrCodePermission/ qrCode / qrCodePermission) are only supported by overseas devices Example 1 of return: pass in -1 for personId { "code": "LAN_SUS-0", "data": { "pageInfo": { "index": 0, "length": 1000, "size": 1, "total": 2 }, "personInfos": [ { "cardAndPasswordPermission": 1,

**Response Format:**


### 3.15 Personnel Feature Information Query

**Method:** `GET` | **URL:** `http://Device IP:8090/person/featureInfo`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person Id | String | Y | Query the person feature information of designated id
| type | Feature type | Int | Y | Registration photo feature value\|Fingerprint feature value

**Notes:** Request data Header domain Body domain Photo Management Interface


## IV. Face/Photo Management


### 4.1 Photo Registration (base64) (Not Recommended)

**Method:** `POST` | **URL:** `http://Device IP:8090/face/create`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Must register person first, 
| faceId | Photo ID | String | Y | If passing in null content for faceId, system will generate a 32-bit faceId whic
| imgBase64 | base64 coding strings of photo | String | Y | Without the header, for example: data:image/jpg;base64,\|Image format supports pn
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu

**Notes:** Note: the picture pixel is greater than 112*112, the resolution is less than 1080p, and the file size is less than 2M Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "123", //The faceId filled in when calling the interface "msg": "Photo added successfully", "result": 1, "success": true }

**Response Format:**


### 4.2 Photo Registration (url) (Not Recommended)

**Method:** `POST` | **URL:** `http://Device IP:8090/ face/createByUrl`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, t
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| imgUrl | Photo url | String | Y | Download image to the local via url, then extract features from the image\|Suppor
| isEasyWay | Select loose or strict photo registration method\|Pixels greater than 112*112, resolution less than 1 | Boolean | N | Not required, \|default as false: test photo quality strictly; \|true: test photo 

**Notes:** Interface description Note: The picture pixel is greater than 112*112, the resolution is less than 1080p, and the file size is less than 2M Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "4e268a87099d46dfa59cd33a75863a03", // Auto-generated 32-bit faceId "msg": "Photo added successfully", "result": 1, "success": true }

**Response Format:**


### 4.3 Photo Registration (base64+url, Android devices are not supported)

**Method:** `POST` | **URL:** `http://Device IP:8090/face`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, t
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| url | Photo url | String | N | If passing in both base64 and url, url first. If passing in url parameter, will 
| base64 | base64 coding strings of photo | String | N | Without the header, such as: data:image/jpg;base64,
| isEasyWay | Loose or strict registration method | Boolean | N | Not required, default as false: strictly detect the photo quality; if passing in
| bbox | Position of face frame, used for extracting features from original registered photos | Json | N | For example: {"bottom": 206, "empty": false, "left": 100, "right": 407, "top":95

**Notes:** Interface description Note: the picture pixel is greater than 112*112, the resolution is less than 1080p, and the file size is less than 2M Request data Header domain Body domain Postman example (base64) Postman example (url) Return example { "code": "LAN_SUS-0", "data": { "faceId": "84bbd2f5117a4591997a0d79968d7e2b", "feature": "qrC1AAAAAAAAA==", //Characteristic value of base64, there is omissio

**Response Format:**


### 4.4 Photo/Feature Values Deletion

**Method:** `POST` | **URL:** `http://Device IP:8090/ face/delete`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| faceId | Photo ID | String | Y | Delete the registered photo of this faceId, which is non-recoverable

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Photo deleted successfully", "result": 1, "success": true }

**Response Format:**


### 4.5 Photo Update (base64)

**Method:** `POST` | **URL:** `http://Device IP:8090/ face/update`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, a
| faceId | Photo ID | String | Y | Content of faceId only allows numbers and English letters, case sensitive, with 
| imgBase64 | base64 coding strings of photo | String | Y | Without the header, such as: data:image/jpg;base64,\|Image format supports png, j
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu

**Notes:** Interface description Note: the picture pixel is greater than 112*112, the resolution is less than 1080p, and the file size is less than 2M Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Photo updated successfully", "result": 1, "success": true }

**Response Format:**


### 4.6 Photo Update (base64+url, not supported on Android devices)

**Method:** `PUT` | **URL:** `http://Device IP:8090/face/`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, a
| faceId | Photo ID | String | Y | Content of faceId only allows numbers and English letters, case sensitive, with 
| url | Photo url | String | N | If passing in both base64 and url, url first. If passing in url parameter, will 
| base64 | base64 coding strings of photo | String | N | Without the header, such as: data:image/jpg;base64,
| isEasyWay | Loose or strict registration method | Boolean | N | Not required, default as false: strictly detect the photo quality; if passing in
| bbox | Position of face frame, used for extracting features from original photos | Json | N | For example: {"bottom": 206, "empty": false, "left": 100, "right": 407, "top":95

**Notes:** Interface description Note: The picture pixel is greater than 112*112, the resolution is less than 1080p, and the file size is less than 2M Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "faceId": "4e268a87099d46dfa59cd33a75863a03", "feature": "qrC1AAAAAAAAAQAA5u ==",//Characteristic value of base64, with omission here "SDKVersion":"general_2

**Response Format:**


### 4.7 Photo Query

**Method:** `POST` | **URL:** `http://Device IP:8090/face/find`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Photo ID | String | Y | Query all registration photos of this person
| base64Enable\|(Overseas devices only) | Whether to get the base64 of the photo | String | N | 1: not get base64 (default)\|2: get base64

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": [ { "cropImgPath": "ftp://192.168.19.73:8010/RegisterPhoto/170ed42886c14a4589a017637d0ff4a9_123_crop.jpg", //Path of sectional drawing "faceId": "123", "feature": "qrC1AAAAAAAAA ==",//Characteristic value of base64, with omission here "SDKVersion":"general_2.0.10.0", //Version number of the algorit

**Response Format:**


### 4.8 Photo-taking Registration

**Method:** `POST` | **URL:** `http://Device IP:8090/face/takeImg`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Take photos for designated person ID\|Person ID must exist; if person ID not exis

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Photo-taking registration mode is enabling, captured photos can be queried according to personId after successful registration. Please complete the registration under guidance", "result": 1, "success": true }

**Response Format:**


### 4.9 Feature Registration (Not supported by Hisilicon device)

**Method:** `POST` | **URL:** `http://Device IP:8090/face/featureReg`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Register a feature for designated person ID\|Person ID must already exist; if thi
| faceId | Photo ID | String | Y | If passing in null content for faceId, system will auto generate faceId and retu
| feature | Feature code | String | Y | Receive via call-back of photo registration, and can also get via photo query In
| featureKey | Secretkey of feature | String | N | Receive via call-back of photo registration after feature registered\|Not verify 
| SDKVersion | Version number of the algorithm | String | N | Version number is the legality verification of registration features, which is s
| Type | Feature type | Int | N | Register feature type:\|1.Face features (by default)\|2.Fingerprint features

**Notes:** Attention: Hisilicon versions will not support this function. Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": { "cropImgPath": "", "faceId": "47122cbd1d3f4f479175538754a54a5f", "feature": "qrC1AAAAAAAAAQ==",//Characteristic value of base64, with omission here "SDKVersion":"general_2.0.10.0", //Version number of algorithm "featureKey": "", "path"

**Response Format:**


### 4.10 Registration Photo Clearing

**Method:** `POST` | **URL:** `http://Device IP:8090/ face/deletePerson`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | Call this Interface, all the registered photo id of this person will be canceled
| personId | Person ID | String | Y | Call this Interface, all the registered photo id of this person will be canceled

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "msg": "Photo cleared successfully", "result": 1, "success": true }

**Response Format:**


### 4.11 Similarity Comparison of Photos

**Method:** `POST` | **URL:** `http://Device IP:8090/photoComparison`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| img1 | base64 coding of photo 1 | String | Y | Without the header, such as: data: image/jpg; base64,\|Device will test the faces
| img2 | base64 coding of photo 2 | String | Y | Without the header, such as: data: image/jpg; base64,\|Device will test the faces

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": 1.0000001, "msg": "Photo compared successfully ", "result": 1, "success": true }

**Response Format:**


### 4.12 Photo Download (Internal interface)

**Method:** `GET` | **URL:** `http://Device IP:8090/download/image`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 
| filename | Picture absolute path | String | Y | Returned by callback and record query interface

**Notes:** Request data Query domain Postman example Recognition Record


## V. Recognition Record Management


### 5.1 Recognition Record Query

**Method:** `GET` | **URL:** `http://Device IP:8090/newFindRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Query personnel recognition records of designated id\|Pass in -1 to query recogni
| startTime | Start time of records | String | Y | If not querying via time, please pass in 0 respectively\|If querying via time, pl
| endTime | End time of records | String | Y | If not querying via time, please pass in 0 respectively\|If querying via time, pl
| length | Max. number in each page | Int | N | Passed-in value of length should be positive Integer between (0,1000]\|If not pas
| model | Types of record | Int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double aut
| order | Sort order | String | N | 1: Ascending order via time\|Not pass in order, default as descending order via t
| index | Page | Int | N | Page starts from 0
| data | String | Remove the escape characters:\|{\|	"address": " No. xxx, xx County, xx City, Zhejiang Province ",\|	"birthday": "1995-11-22",\|	"compareResult": false,\|	"createTime": 1600426322501,\|	"id": 0,\|	"idNum": "33108119000000000",\|	"issuingOrgan": "XXX",\|	"name": "XXX",\|	"nation": "Han",\|	"photoPath": "ftp://...",\|	"sex": "Male",\|	"usefulLife": "2012.02.12-2022.02.12"\|} | Info on ID card\|address: Family address,\|birthday: Date of birth,\|compareResult: Result of comparison,\|createTime: Time of recognition,\|id: Non-sense,\|idNum: ID number,\|issuingOrgan: Place of issuing,\|name: Name,\|nation: Nationality,\|photoPath: Photo on ID card,\|sex: Gender,\|usefulLife: Validity of ID card | 

**Notes:** Request data Query domain Postman example Return example Hisilicon device returns as follows: { "code": "LAN_SUS-0", "data": { "pageInfo": { "index": 0, "length": 1000, "size": 1, "total": 3 }, "records": [ { "aliveType": 1, "idcardNum": "362226199100", "id": 5, "identifyType": 1, "isImgDeleted": 0, "isPass": true, "model": 0, "name": "A Liang", "passTimeType": 3, "path": "ftp://192.168.18.17:8010

**Response Format:**


### 5.2 Recognition Record Deletion

**Method:** `POST` | **URL:** `http://Device IP:8090/newDeleteRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| personId | Person ID | String | Y | Delete recognition records of designated id\|Pass in -1 to delete recognition rec
| startTime | Start time of records | String | Y | To delete all face recognition records and on-site photos within time period \|Pa
| endTime | End time of records | String | Y | To delete all face recognition records and on-site photos within time period\|Pas
| model | Types of records | Int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double aut

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "Number of recognition records to delete: 2", "msg": "Deleted successfully", "result": 1, "success": true }

**Response Format:**


### 5.3 Recognition Record Deletion (via Unix Millisecond Timestamp)

**Method:** `POST` | **URL:** `http://Device IP:8090//newDeleteRecordsByUnixTime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| Pass | Device password | String | Y | 
| personId | Person ID | String | Y | Delete recognition records of designated id\|Pass in -1 to delete recognition rec
| startTime | Start time of records | String | Y | Delete all face recognition records and on-site photos within time period\|Pass i
| endTime | End time of records | String | Y | Delete all face recognition records and on-site photos within time period\|Pass i
| Model | Types of records | Int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double aut

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "Number of recognition records to delete: 2", "msg": "Deleted successfully", "result": 1, "success": true }

**Response Format:**


### 5.4 Face Recognition Record Query

**Method:** `GET` | **URL:** `http://Device IP:8090/findRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Pass | Device password | String | Y | 
| personId | Person ID | String | Y | Query recognition records of designated id\|Pass in -1 to query recognition recor
| startTime | Start time of records | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| endTime | End time of records | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| Length | Maximum quantity per page | Int | Y | Pass in -1 for no paging\|Not passing -1, please keep greater than 0
| Index | Page | Int | Y | Page starts from 0

**Notes:** Request data Query domain Postman example Return example { "code": "LAN_SUS-0", "data": { "pageInfo": { "index": 0, "length": 1000, "size": 1, "total": 3 }, "records": [ { "aliveType": 1, "idcardNum": "362226199100", "id": 5, "identifyType": 1, "isImgDeleted": 0, "isPass": true, "model": 0, "name": "ALiang", "passTimeType": 3, "path": "ftp://192.168.18.17:8010/IdentifyRecords/2019-09-30/3_20190930

**Response Format:**


### 5.5 Delete facial recognition records

**Method:** `POST` | **URL:** `http://Device IP:8090/deleteRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| time | Record end time | String | Y | If all portrait recognition records and on-site photos before the uploaded date 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": " "msg": " successfully deleted ", "result": 1, "success": true }

**Response Format:**


### 5.6 Delete facial recognition records (delete via Unix millisecond time stamp)

**Method:** `POST` | **URL:** `http://Device IP:8090/deleteRecordsByUnixTime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| Pass | device password | String | Y | 
| unixTime | Record end time | String | Y | If all portrait recognition records and on-site photos before the uploaded date 

**Response Format:**


### 5.7 Card record query

**Method:** `GET` | **URL:** `http://Device IP:8090/findICRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Pass | Device password | String | Y | 
| personId | Personnel ID | String | Y | Query the personnel identification record of the specified id\|Enter -1 to query 
| startTime | Record start time | String | Y | If you do not query by time, please pass in 0 respectively\|If you need to query 
| endTime | Record end time | String | Y | If you do not query by time, please pass in 0 respectively\|If you need to query 
| Length | Maximum number per page | int | Y | Pass in -1 for no page break\|If you do not pass -1, please be greater than 0
| Index | Page | int | Y | page number, starting from 0

**Notes:** Request data Query domain Postman example Return example { "code": "LAN_SUS-0", "data": { "pageInfo": { "index": 0, "length": 1000, "size": 1, "total": 3 }, "records": [ { "aliveType": 1, "idcardNum": "362226199100", "id": 5, "identifyType": 1, "isImgDeleted": 0, "isPass": true, "model": 0, "name": "Aliang", "passTimeType": 3, "permissionTimeType": 3, "path": "ftp://192.168.18.17:8010/IdentifyReco

**Response Format:**


### 5.8 Deletion of card records

**Method:** `POST` | **URL:** `http://Device IP:8090/deleteICRecords`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| Pass | Device password | String | Y | 
| Time | Time nodes | String | Y | If you delete all card identification records before the date and time point upl

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": " "msg": "successfully deleted", "result": 1, "success": true }

**Response Format:**


### 5.9 Deletion of card swiping records (deleted by Unix millisecond time stamp)

**Method:** `POST` | **URL:** `http://device IP:8090/deleteICRecordsByUnixTime`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| unixTime | Record end time | String | Y | If you delete all card identification records before the uploaded date and time\|

**Notes:** Request data Header domain Body domain Postman example Return example { "msg": "successfully deleted", "result": 1, "success": true } Ⅵ. Rule management

**Response Format:**


## VI. Rule Management


### 6.1 Add rule

**Method:** `POST` | **URL:** `http://device IP:8090/rule/create`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| Pass | Device password | String | Y | 
| ruleId | Rule id | String | Y | Unique identification, cannot be repeated
| Type | Rule type | Int | Y | 1: time rules
| Name | Rule name | String | N | If not filled default as ruleId
| content | Rule content | json | Y | {\|	"endAt": 1653703768298,\|	"startAt": 1651889321428,\|	"day": [\|		{\|			"endAt": 
| startAt | Rule validity period start time | Int | Y | Time when the rule starts to take effect (unix time, in ms)
| endAt | Rule validity period end time | Int | Y | Rule expiration time (unix time, in ms)
| Day | Day rule | Object[] | N | Rules by day dimension (if this rule is set, all parameters under the object mus
| +startAt | Days - Validity period start time | Int | N | Time when the rule starts to take effect (unix time, in ms)
| +endAt | days - expiration date | Int | N | Rule expiration time (unix time, in ms)
| +segment | period | Object[] | N | Valid period (must be even and > 0)
|  |  | String | N | time period content such as  ["19:00:00","19:59:59"]
| Week | weekly rules | Object[] | N | Rules by week dimension (if this rule is set, all parameters under the object mu
| +startAt | week - validity period start time | Int | N | Time when the rule starts to take effect (unix time, in ms)
| +endAt | week - expiration date | Int | N | Rule expiration time (unix time, in ms)
| +content | Weekly rules content | Object[] | N | content
| ++dayweek | week | Int | N | week(1\2\3\4\5\6\7)
| ++segment | Period | Object[] | N | Valid period (must be even and > 0)
|  |  | String | N | time period content such as  ["19:00:00","19:59:59"]

**Notes:** Request data Header domain Body domain Content parameters Return example { "code": "LAN_SUS-0", "data": { "ruleId": "xxxxx", "name": "hello", ...... }, "msg": " Successful operation ", "result": 1, "success": true }

**Response Format:**


### 6.2 Delete rule

**Method:** `POST` | **URL:** `http://device IP:8090/rule/delete`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| Pass | Device password | String | Y | 
| isDeleteAll | Whether to delete all rules | Int | N | 1: delete all rules, non-1: delete rules in ruleId; when deleting all rules, the
| ruleId | Rule id | Object[] | Y | 
|  |  | String | Y | Pass ["xxx", "yyy"] to delete the rule with id "xxx","yyy".

**Notes:** Request data Header domain Body domain Return example { "code": "LAN_SUS-0", "data": { "rule": [ { "ruleId": "xxxxxx", "result": true }, ...... ] }, "msg": " Successful operation", "result": 1, "success": true }

**Response Format:**


### 6.3 Update rules

**Method:** `POST` | **URL:** `http://device IP:8090/rule/update`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| ruleId | Rule id | String | Y | Unique identifier, not repeatable
| type | rule type | Int | N | 
| name | rule name | String | N | Do not pass and keep the last value
| content | Rule content | json | N | Do not pass and keep the last value (refer to the description of content in 6.1)

**Notes:** Request data Header domain Body domain Return example { "code": "LAN_SUS-0", "data": { "ruleId": "xxxxx", "name": "hello", ...... }, "msg": " Successful operation", "result": 1, "success": true }

**Response Format:**


### 6.4 Query rules

**Method:** `GET` | **URL:** `http://device IP:8090/rule/find`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| type | rule type | Int | N | 
| name | rule name | String | N | 
| startAt | Rule effective start time | Int | N | unix time, in ms
| endAt | Rule effective end time | Int | N | unix time, in ms
| page | page properties | Object | Y | 
| pageNum |  | Int | Y | Pages start at 1
| limit |  | Int | Y | Quantity per page
| sort | to sort | Boolean | N | Sort, false-descending true-ascending

**Notes:** Request data Header domain Body domain Return example { "code": "LAN_SUS-0", "data": { "total": 100, "list": [ { "ruleId": "xxxxxx", "name": " time rule 1", "type": 1, "endAt": 1652753373654, "startAt": 1652580573654 }, ...... ] }, "msg": " Successful operation", "result": 1, "success": true }

**Response Format:**


### 6.5 Get rule details

**Method:** `POST` | **URL:** `http://device IP:8090/rule/detail`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | device password | String | Y | 
| ruleId | Rule id | String | Y | 

**Notes:** Request data Header domain Body domain Return example { "code": "LAN_SUS-0", "data": { "ruleId": "xxxxxx", "name": "time rule 1", "type": 1, "content": "", "endAt": 1652753373654, "startAt": 1652580573654 }, "msg": "Successful operation", "result": 1, "success": true } Ⅶ. Heartbeat Mechanism Attention: All Hisilicon devices support this mechanism, and several versions of Android devices support it

**Response Format:**


## VII. Callback


### 7.1 Device Heartbeat Callback

**Method:** `POST` | **URL:** `http://Device IP:8090/setDeviceHeartBeat`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Platform address | String | Y | Device will request following fields via POST from the interface in every 1 minu
| interval | Unit of heartbeat interval: second | Int | N | Not pass in or pass in null, heartbeat Interval will be 60s by default\|Suggested
| deviceKey | String | Device serial number | "deviceKey":"84E0F4200CA602FA" | 
| time | String | Millisecond timestamp of device current time | "time":"1537236693823" | 
| ip | String | Current device IP address | "ip":"192.168.20.66" | 
| personCount | String | Number of people in the device | "personCount":"2" | 
| faceCount | String | Number of photos in the device | "faceCount":"3" | 
| fingerCount | String | Number of fingerprints in the device | " fingerCount ":"1" | 
| version | String | Device version number | "version":"3.6203" | 
| freeDiskSpace | String | Free space of Disk, unit: M | "freeDiskSpace":"4546.56" | 
| cpuUsageRate | String | CPU usage rate, unit: % | "cpuUsageRate":"46.206898" | 
| cpuTemperature | String | CPU temperature, unit: ℃ | "cpuTemperature":"76.0" | 
| memoryUsageRate | String | Memory usage rate, unit: % | "memoryUsageRate":"76.206898" | 
| deviceName | String | Device name | "deviceName":"Real Intelligent" | 
| SDKVersion | String | Version number of device algorithm | "SDKVersion":"v0.13.11.e2989-\|1180907.256-20190613-\|general.2.0.5.0" | 
| companyName | String | Company name | "companyName":"face recognition system" | 
| deviceKey | String | Exclusive mark of device |  | 
| time | String | Current timestamp of device |  | 
| ip | String | Current IP address of device |  | 
| personCount | String | Number of registered personnel in device |  | 
| faceCount | String | Number of registered photos in device |  | 
| fingerCount | String | Number of fingerprints in the device |  | 
| version | String | Device version number |  | 
| freeDiskSpace | String | Remaining disk space, unit: M |  | 
| cpuUsageRate | String | Usage rate of CPU, unit: % |  | 
| cpuTemperature | String | CPU temperature, unit: ℃ |  | 
| memoryUsageRate | String | Usage rate of memory, unit: % |  | 
| deviceName | String | Device name |  | 
| SDKVersion | String | Version of algorithm |  | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "http://192.168.16.250:8888/lan/heartBeatCallback", "msg": "Set successfully", "result": 1, "success": true } Field specification of device heartbeat call-back parameter 7.1.1 Instruction for Heartbeat Data Sent by <Device> to <Report Platform Address> Attention: Data reported to the platform will 

**Response Format:**


### 7.2 Address Setting for Obtaining Tasks (SetTaskInterfaceAddress)

**Method:** `POST` | **URL:** `http://Device IP:8090/setTaskInterfaceAddress`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Platform address | String | Y | 
| deviceKey | String | Exclusive mark of the device |  | 
| taskNo | Name of task | String | Y | Custom naming
| interfaceName | Interface name | String | Y | setPassWord
| result | Whether to handle | Boolean | Y | Default as true
| ... | ... | ... | ... | ...
| ... | ... | ... | ... | ...
| ... | ... | ... | ... | ...
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setPassWord
| result | Whether to handle | Boolean | Y | Default as true
| oldPass | Old password | String | Y | New devices or reset devices, before calling other interfaces, need to have init
| newPass | New password | String | Y | New devices or reset devices, before calling other interfaces, need to have init
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | getDeviceKey
| result | Whether to handled | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setConfig
| result | Whether to handle | Boolean | Y | Default as true
| config | Configuration collections | JSON | Y | Pass in {} for config, all configured parameters will be restored to default \|Pa
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/config
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setStrangerOutInfo
| result | Whether to handle | Boolean | Y | Default as true
| config | Recognition mode configuration set | Json | Y | {\|"recDoubleValue":70,\|"regInterval":2000,\|"recType": 1,\|"recDisplayImageMode":1
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setStrangerOutInfo
| result | Whether to handle | Boolean | Y | Default as true
| relaySwitch | Relay switch control | Int | Y | Custom content 0: Off\|1: On (Relay door opening for second-generation device )
| serialOutMode | Serial port output type | Int | Y | 0: Off\|1: Door opening (Serial port door opening for first-generation device)\|2:
| serialOutContent | Serial port custom content | String | Y | Serial port custom content. Only allow numbers, English and English characters, 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | widgetConfig
| result | Whether to handle | Boolean | Y | Default as true
| showIp | Device IP | Int | Y | 0: Display (by default)\|1: Hide
| showDeviceKey | Device serial number | Int | Y | 0: Display (by default)\|1: Hide
| showPeopleNum | Users/Photos | Int | Y | 0: Display (by default)\|1: Hide
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | changeLogo
| result | Whether to handle | Boolean | Y | Default as true
| imgBase64 | Base64 code strings of logo image | String | Y | Without the header, such as: data:image/jpg;base64,\|Pass in-1 to clear img2 set 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/img1
| result | Whether to handle | Boolean | Y | Default as true
| base64 | Base64 code string of img1 | String | Y | Without the header, such as: data:image/jpg;base64,\|Pass in-1 to clear img1 set 
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | setNetInfo
| result | Whether to handle | Boolean | Y | Default as true
| isDHCPMod | DHCP mode selection | Int | Y | The device defaults to DHCP mode, which automatically obtains the IP address\|Pas
| ip | Ip address | String | N/Y | The IP field name must be passed in lowercase, and the IP cannot be greater than
| gateway | Gateway | String | N/Y | 
| subnetMask | Subnet mask | String | N | 
| DNS | DNS server | String | N/Y | 
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | setWifi
| result | Whether to handle | Boolean | Y | Default as true
| wifiMsg | Collection of wireless configuration information | Json | Y | Auto obtain IP\|{"ssId":"TP-LINK_E2.4G","pwd":"test-1234","isDHCPMod":true}\|Fixed
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setTime
| result | Whether to handle | Boolean | Y | Default as true
| timestamp | Unix millisecond timestamp | String | Y | After successful configuration, device will refresh its time (refresh every minu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/screenSaverTime
| result | Whether to handle | Boolean | Y | Default as true
| time | Enter standby time of screen protector (unit: minute) | Int | Y | Set the standby time as 3min by default, unit in minute.\|\|Pass in value between 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | restartDevice
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/reset
| result | Whether to handle | Boolean | Y | Default as true
| delete | Select to delete | Boolean | Y | Delete all recognition records, registration photos, on-site photos, personnel i
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/upgrade
| result | Whether to handle | Boolean | Y | Default as true
| url | Download OTA upgrade package | String | Y | Visit this url when calling the interface, if url can be accessed, then device s
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setIdentifyCallBack
| result | Whether to handle | Boolean | Y | Default as true
| callbackUrl | Call-back address | String | Y | When the device recognizes person successfully, it will request following fields
| base64Enable | base64 switch of on-site photos | int | N | 1: Off (by default) 2: On
| taskNo | Task name | String | Y | Custom naming
| interfaceName | Interface name | String | Y | setImgRegCallBack
| result | Whether to handle | Boolean | Y | Default as true
| url | Callback address | String | Y | When photo registered successfully (including device-taking photo registration),
| base64Enable | On-site photo base64 switch | int | N | 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setDeviceHeartBeat
| result | Whether to handle | Boolean | Y | Default as true
| url | Call-back address | String | Y | Device will request these fields via POST: deviceKey, time, ip, personCount, fac
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/callback
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/openDoorControl
| result | Whether to handle | Boolean | Y | Default as true
| type | Interaction type of device | Int | N | 1: Open the door 2: Serial port 3: Wiegand 4: Custom text pop-up, custom voice b
| content | Output content | String | N | type=2: serial port, allow numbers, English and English characters, with the lim
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | setCardRegCallBack
| result | Whether to handle | Boolean | Y | Default as true
| url | Call-back address | String | Y | When card number registration is succeeded (including device enrolling card numb
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | getSDKVersion
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/information
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | device/getIdentifyModel
| result | Whether to handle | Boolean | Y | Default as true
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/create
| result | Whether to handle | Boolean | Y | Default as true
| person | Collection of personnel information | Json | Y | Json example:\|{\|"id":"001",\|"name":"",\|"idcardNum":"",\|"iDNumber":"",\|"facePermi
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/delete
| result | Whether to handle | Boolean | Y | Default as true
| id | Person ID | String | Y | If deleting multiple personnel, join their id with English commas,Pass in -1 to 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/update
| result | Whether to handle | Boolean | Y | Default as true
| person | Collection of personnel information | Json | Y | {\|"id":"001",\|"name":"",\|"idcardNum":"",\|"iDNumber":"",\|"iDNumberPermission":2,\|
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/find
| result | Whether to be handled | Boolean | Y | Default as true
| id | Person ID | String | Y | Query person information of designated id\|Passing in -1 for id to query all pers
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/findByPage
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Query person information of designated id \|Passing in -1 for id to query all per
| length | Max. number in each page | int | N | Passed-in value of length requires positive integers between (0,1000]\|If not pas
| index | Page | int | N | Page starts from 0. Passed-in value of index must be less than total pages, for 
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/icCardRegist
| result | Whether to be handled | Boolean | Y | Default as true
| personId | Person ID | String | Y | Register card number for designated person ID\|Person ID must exist; if ID not ex
| taskNo | Task name | String | Y | Custom name
| interfaceName | Interface name | String | Y | person/createPasstime
| result | Whether to handle | Boolean | Y | Default as true
| passtime | The time period that a person is allowed to enter every day | String | Y | {"personId":"9eecc839cd7941c5a4d3165202dd3c32","passtime":"09:00:00,10:00:00,17:
| taskNo | Task name | String | Y | Custom name
| interfaceName | Interface name | String | Y | person/passtime
| result | Whether to handle | Boolean | Y | Default as true
| passtime | Allowed passtime for a person every day | String | Y | {"passtime":"09:00:00,10:00:00,17:00:00,17:30:00,18:30:00,20:25:00"}\|The range i
| personId | Person Id | String | Y | If the passtime of multiple personnel is set, the personId is separated by Engli
| taskNo | Task name | String | Y | Custom name
| interfaceName | Interface name | String | Y | person/deletePasstime
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person Id | String | Y | Delete the passtime permission setting of the person, and the person no longer h
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/permissionsCreate
| result | Whether to handle | Boolean | Y | Default as true
| time | Time of expiry date, delete this person regularly | String | Y | Subject to device system time, when person permission is expired, this person wi
| personId | Person Id | String | Y | Support single person only
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/permissionTime
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person Id | String | Y | If setting the permission time for multiple personnel, join personId with Englis
| startTime | Start time | String | Y | Format of passed-in time is (Year-Month-Day Hour: Minute: Second): 2017-07-15 12
| endTime | End time | String | Y | Format of passed-in time is (Year-Month-Day Hour: Minute: Second): 2017-07-15 12
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/permissionsDelete
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person Id | String | Y | To delete permission time of multiple personnel, join personId with English comm
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | person/permissionInfo
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person Id | String | Y | Query person info of designated id \|Pass in -1 for id to query all personId
| length | Max. numbers in each page | Int | N | Passed-in value of length requires positive integer between (0,1000],\|If not pas
| index | Page | Int | N | Page starts from 0, passed-in value of index must be less than total number of p
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/create
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Must register person first, 
| faceId | Photo ID | String | Y | If passing in null content for faceId, system will generate a 32-bit faceId whic
| imgBase64 | base64 coding strings of photo | String | Y | Without the header, for example: data: image/jpg; base64,\|Image format supportsp
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/createByUrl
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person Id | String | Y | Used to mark that this photo belongs to a person id\|Register the person first be
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| imgUrl | Photo url | String | Y | Download image to the local via url, extract features from the image\|Support ima
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, b
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| url | Photo url | String | N | If passing in both base64 and url, url first. If passing in url parameter, will 
| base64 | base64 coding strings of photo | String | N | Without the header, for example: data: image/jpg; base64,
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/delete
| result | Whether to  handle | Boolean | Y | Default as true
| faceId | Photo ID | String | Y | Delete registered photos of this faceId, which are nonrecoverable
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/update
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first, b
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| imgBase64 | base64 coding strings of photo | String | Y | Without the header, such as: data:image/jpg;base64,\|Image format supports png, j
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Used to mark that this photo belongs to a person id\|Register the person first be
| faceId | Photo ID | String | Y | If passing in null content for faceId, the system will generate a 32-bit faceId 
| url | Photo url | String | N | If passing in both base64 and url, url first. If passing in url parameter, will 
| base64 | base64 coding strings of photo | String | N | Without the header, such as: data: image/jpg; base64,
| isEasyWay | Select loose or strict photo registration method | Boolean | N | Not required, default as false: test photo quality strictly; true: test photo qu
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/find
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Photo ID | String | Y | Query all the registered photos of this person
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/takeImg
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Take photos for designated person ID\|Person ID must exist; if this person ID not
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/featureReg
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Register a feature for designated person ID\|Person ID must exist; if person id d
| faceId | Photo ID | String | Y | If passed-in content of faceId is null, system will auto generate faceId and ret
| feature | Feature code | String | Y | Receive via call-back of photo registration, and also obtain via photo query int
| featureKey | Secretkey of feature | String | N | Receive via call-back of photo registration after features registered\|Not verify
| SDKVersion | Version number of the algorithm | String | N | Version number is the legality verification of registration features, which is s
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | face/deletePerson
| result | Whether to be handled | Boolean | Y | Default as true
| personId | Person ID | String | Y | Call this interface, all the registered photo id of this person will be canceled
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | photoComparison
| result | Whether to  handle | Boolean | Y | Default as true
| img1 | base64 coding of photo 1 | String | Y | Without the header, such as: data: image/jpg; base64,\|Device will test the faces
| img2 | base64 coding of photo 2 | String | Y | Without the header, such as: data: image/jpg; base64,\|Device will test the faces
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | newFindRecords
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Query personnel recognition records of designated id\|Pass in -1 to query recogni
| startTime | Start time of record | String | Y | If not query via time, please pass in 0 respectively\|If query via time, please f
| endTime | End time of record | String | Y | If not query via time, please pass in 0 respectively\|If query via time, please f
| length | Max. number in each page | int | N | Pass in positive integers (0,1000] for value of length\|If not passing in length,
| model | Record type | int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double ver
| order | Sort order | String | N | 1: Ascending order via time\|Not passing in order, descending order via time by d
| index | Page | int | N | Page starts from 0
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | newDeleteRecords
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Delete recognition records of designated id\|Pass in -1 to delete recognition rec
| startTime | Start time of record | String | Y | To delete all face recognition records and on-site photos within time period \|Pa
| endTime | End time of record | String | Y | To delete all face recognition records and on-site photos within time period\|Pas
| model | Types of record | int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double aut
| taskNo | Name of task | String | Y | Custom the name
| interfaceName | Name of interface | String | Y | newDeleteRecordsByUnixTime
| result | Whether to  handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Delete recognition records of designated id\|Pass in -1 to delete recognition rec
| startTime | Start time of record | String | Y | Delete all face recognition records and on-site photos within time period\|Pass i
| endTime | End time of record | String | Y | Delete all face recognition records and on-site photos within time period\|Pass i
| model | Types of record | int | N | -1: All types of recognition records\|0: Face recognition\|1: Face&Card double aut
| personId | Person ID | String | Y | Delete recognition records of designated id\|Pass in -1 to delete recognition rec
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | findRecords
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Query the personnel recognition record of the specified ID\|Pass in -1 to query t
| startTime | Record start time | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| endTime | Record end time | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| length | Maximum quantity per page | int | Y | Pass in -1 for no paging\|If not passing -1, please keep the value greater than 0
| index | Page | int | Y | Page starts from 0
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | deleteRecords
| result | Whether to handle | Boolean | Y | Default as true
| time | Record end time | String | Y | If deleting all face recognition records and on-site photos before the passed-in
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | deleteRecordsByUnixTime
| result | Whether to handle | Boolean | Y | Default as true
| unixTime | Record end time | String | Y | If deleting all face recognition records and on-site photos before the passed-in
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | findICRecords
| result | Whether to handle | Boolean | Y | Default as true
| personId | Person ID | String | Y | Query the personnel recognition record of the specified ID\|Pass in -1 to query t
| startTime | Record start time | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| endTime | Record end time | String | Y | If not query by time, please pass in 0 respectively\|If query by time, please fol
| length | Maximum quantity per page | int | Y | Pass in -1 for no paging\|If not pass in -1, please keep the value greater than 0
| index | Page | int | Y | Page starts from 0
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | deleteICRecords
| result | Whether to handle | Boolean | Y | Default as true
| time | Time node | String | Y | If deleting all card verification records before the passed-in date\|The passed-i
| taskNo | Task name | String | Y | Custom the name
| interfaceName | Interface name | String | Y | deleteICRecordsByUnixTime
| result | Whether to handle | Boolean | Y | Default as true
| unixTime | Record end time | String | Y | If deleting all card records before the passed-in date\|The passed-in time format

**Notes:** Request data Header domain Body domain Postman example Return example { "code":"LAN_SUS-0", "data":"http://www.baidu.com", "msg":"Set successfully", "result":1, "success":true } 7.2.1 Instrcution for Parameter Fields that Device Requested for <Platform Address> Attention: Data is in the body. Data example { "deviceKey": "xxxxxxx" } 7.2.2 Example of [Task Data] Obtained from the Requesting <Report 

**Response Format:**


### 7.3 Report Address for the Result of Task Processing (SetTaskProcessingResultAddress)

**Method:** `POST` | **URL:** `http://Device IP:8090/setTaskProcessingResultsAddress`

**Request Parameters:**

| Parameter | Description | Type | Required | Additional
|---|---|---|---|---
| Content-Type | Designate the request type of media | String | Y | application/x-www-form-urlencoded
| pass | Device password | String | Y | 
| url | Report address | String | Y | Device will call this interface to return processing results after finishing the
| deviceKey | String | Exclusive mark of device |  | 
| result | String | Processing results |  | 
| taskNo | String | Number of tasks |  | 
| taskNo | String | Serial number of the task, corresponds to the number of the issued task |  | 
| interfaceName | String | Name of interface |  | 
| result | String | Returned content from the interface of adding personnel |  | 

**Notes:** Request data Header domain Body domain Postman example Return example { "code": "LAN_SUS-0", "data": "http://192.168.79.192:8010/api/TaskResult ", "msg": "Set successfully", "result": 1, "success": true } 7.3.1 Instrcution for Data Fields of Task Processing Results that Device Sent to <Report Address> Attention: Data is in body, format of Json replied in result parameters should keep consistent wi

**Response Format:**


---
*Generated from DEVICE LAN VERSION INTERFACE DOCUMENT V5.1.14 - Total 109 endpoints*
