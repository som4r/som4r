/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package robot.wvapp_veiculo;

import android.app.Activity;
import android.content.Context;
import android.content.pm.ActivityInfo;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.os.Vibrator;
import android.view.View;
import android.webkit.JsResult;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.EditText;

/**
 *
 * @author marcus
 */
public class MainActivity extends Activity implements SensorEventListener {

    private WebView mWebView;
    private EditText mEditText;
    private Handler mHandler = new Handler();
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private PowerManager mPowerManager;
    private WakeLock mWakeLock;
    private float accX = 0f;
    private float accY = 0f;
    private long accId = 0l;
    private Vibrator mVibrator;

    @Override
    public void onCreate(Bundle icicle) {
        super.onCreate(icicle);

        // Get an instance of the SensorManager
        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);

        // Get an instance of the PowerManager
        mPowerManager = (PowerManager) getSystemService(POWER_SERVICE);
        // Create a bright wake lock
        mWakeLock = mPowerManager.newWakeLock(
                PowerManager.SCREEN_DIM_WAKE_LOCK, getClass().getName());
        mWakeLock.acquire(); //SCREEN_DIM_WAKE_LOCK

        // Vibrate the mobile phone
        mVibrator = (Vibrator) this.getSystemService(Context.VIBRATOR_SERVICE);

//        mEditText = (EditText) findViewById(R.id.EditText01);
//        String webViewUrl = "http://"
//                + mEditText.getText().toString().trim()
//                + "/wv_veiculo/index.php";

        setContentView(R.layout.main);
        mWebView = (WebView) findViewById(R.id.webview);

        WebSettings webSettings = mWebView.getSettings();
        webSettings.setSavePassword(false);
        webSettings.setSaveFormData(false);
        webSettings.setJavaScriptEnabled(true);
//        webSettings.setSupportZoom(true);

        mWebView.setWebChromeClient(new MyWebChromeClient());

        mWebView.addJavascriptInterface(new MyJavaScriptInterface(), "jsinterface");

        mWebView.loadUrl("http://192.168.20.101/wv_veiculo/index.php");
    }

    @Override
    protected void onResume() {
        super.onResume();
        mSensorManager.registerListener(this, mAccelerometer, 
                SensorManager.SENSOR_DELAY_UI);
        mWakeLock.acquire();
    }

    @Override
    protected void onPause() {
        super.onPause();
        mSensorManager.unregisterListener(this);
        mWakeLock.release();
    }

    @Override
    protected void onStop() {
        super.onStop();
        mWakeLock.release();
    }

    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    final class MyJavaScriptInterface {

        private String AccX = "0";
        private String AccY = "0";
        private String AccId = "0";
        //private boolean sensorEnabled = false;

//        public boolean isSensorEnabled() {
//            return sensorEnabled;
//        }
//
//        public void setSensorEnabled(boolean sensorEnabled) {
//            this.sensorEnabled = sensorEnabled;
//        }

        public String getAccX() {
            return AccX;
        }

        public void setAccX(String AccX) {
            this.AccX = AccX;
        }

        public String getAccY() {
            return AccY;
        }

        public void setAccY(String AccY) {
            this.AccY = AccY;
        }

        public String getAccId() {
            return AccId;
        }

        public void setAccId(String AccId) {
            this.AccId = AccId;
        }

        /**
         * This is not called on the UI thread. Post a runnable to invoke
         * loadUrl on the UI thread.
         */
        public void refreshSensorData() {

            setAccX(String.valueOf(accX));
            setAccY(String.valueOf(accY));
            setAccId(String.valueOf(accId));
//            mHandler.post(new Runnable() {
//
//                public void run() {
//                    // Atualizando valores lidos.
//                    setAccX(String.valueOf(accX));
//                    setAccY(String.valueOf(accY));
//                    setAccId(String.valueOf(accId));
//                    mWebView.loadUrl("javascript:doSensorAction()");
//                }
//            });

        }

        public void doVibrate(int milliSeconds) {
            mVibrator.vibrate(
                (milliSeconds>0 && milliSeconds < 2000 ? milliSeconds : 200));
        }

        public void clickOnAndroid() {
            mHandler.post(new Runnable() {

                public void run() {
//                    setVelocidade(String.valueOf(Integer.parseInt(getVelocidade()) + 1));
                    mWebView.loadUrl("javascript:wave()");
                }
            });

        }


    }

    /**
     * Provides a hook for calling "alert" from javascript. Useful for
     * debugging your javascript.
     */
    final class MyWebChromeClient extends WebChromeClient {

        @Override
        public boolean onJsAlert(WebView view, String url, String message, JsResult result) {
//            Log.d(LOG_TAG, message);
            result.confirm();
            return true;
        }
    }

    public void onSensorChanged(SensorEvent event) {
        accX = event.values[0];
        accY = event.values[1];
        accId = event.timestamp;
    }

        // This method is called at button click because we assigned the name to the
    // "On Click property" of the button
//    public void myClickHandler(View view) {
//        switch (view.getId()) {
//            case R.id.Button01:
//                mEditText = (EditText) findViewById(R.id.EditText01);
//                String webViewUrl = "http://"
//                    + mEditText.getText().toString().trim()
//                    + "/wv_veiculo/index.php";
//                mWebView = (WebView) findViewById(R.id.webview);
//                mWebView.loadUrl(webViewUrl);
//                break;
//        }
//    }
}
