# Basics
Bambu Handy and Bambu Studio support printer binding through `user_bind.py` code.

It currently supports binding of Chinese and Asian accounts.

I can't connect my region lock printer to another region account yet. There's a lot of community content in this area, but there seems to be no detour and clear resolution yet
## Install Python Package
```plaintext 
 pip install requests binascii jwt==1.7.1 
 ```

## Code Execution
After installing the package, enter python3 `user_bind.py` in the path where you want to run the code.

Run the code and enter the printer IP address, Bambu account email, or Chinese phone number (no country code +86), password.

Finally, the Login `Login Report status: SUCCESS, reason: None` log is displayed and the printer is linked to the account

If you want to clear the binded device, if you run the code while binded, it says it is already binded and asks for unbind.
Enter True to ask for the device ID to unbind. After entering, the device is unbinded.

## Support
Unexpected failure reason These messages mean region lock

- The device IP is limited. Please contact our customer service.
- The device region is limited. Please make sure your printer is in correct region.

For the P1/A1(Mini) series, even if I use the right account for the printer area, it seems to be blocked by IP lock even if the actual area is different. In this case, try using Chinese vpn when executing my code

If you encounter an error when you read the explanation and meet the conditions, please register the issue with the log.
[Github issue page](https://github.com/lunDreame/BambuProject/issues)
