package com.bianosomequipadora.sokkerpro;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        WebView view = new WebView(this);
        view.setWebViewClient(new WebViewClient());
        WebSettings settings = view.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setBuiltInZoomControls(false);
        view.loadUrl("https://bianosomequipadora-cpu.github.io/sokkerpro-host/painel.html?app=android");
        setContentView(view);
    }
    @Override public void onBackPressed() { WebView v=(WebView)findViewById(android.R.id.content); super.onBackPressed(); }
}
