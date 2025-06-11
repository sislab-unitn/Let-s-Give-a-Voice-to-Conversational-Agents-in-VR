using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using UnityEditor;
using System;
using System.Globalization;
public class Timer : MonoBehaviour
{
    

    public DateTime time;
    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void startTimer(){
        time = DateTime.Now;
    }

    public void stopTimer(){
        DateTime time2 = DateTime.Now;
        TimeSpan timeSpan = time2.Subtract(time);
        Debug.Log(timeSpan.TotalMilliseconds);
    }
}
