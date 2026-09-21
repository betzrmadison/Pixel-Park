package com.pixelpark;

import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.vehicle.VehicleMoveEvent;
import org.bukkit.entity.Minecart;
import org.bukkit.Bukkit;

import java.io.OutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;

public class PixelParkCore extends JavaPlugin implements Listener {

    private static final String BACKEND_URL = "http://localhost:8000/api/telemetry";
    private final Gson gson = new Gson();

    private long lastSendTime = 0;
    private static final long THROTTLE_MS = 100; // 10 updates per sec max

    @Override
    public void onEnable() {
        getLogger().info("Pixel Park Core booted successfully!");
        getServer().getPluginManager().registerEvents(this, this);
    }

    @EventHandler
    public void onMinecartMove(VehicleMoveEvent event) {
        if (!(event.getVehicle() instanceof Minecart)) {
            return;
        }

        long now = System.currentTimeMillis();
        if (now - lastSendTime < THROTTLE_MS) {
            return;
        }
        lastSendTime = now;

        Minecart cart = (Minecart) event.getVehicle();

        Map<String, Object> payloadMap = new HashMap<>();
        payloadMap.put("cart_id", cart.getUniqueId().toString());
        payloadMap.put("x", Math.round(event.getTo().getX() * 100.0) / 100.0);
        payloadMap.put("y", Math.round(event.getTo().getY() * 100.0) / 100.0);
        payloadMap.put("z", Math.round(event.getTo().getZ() * 100.0) / 100.0);
        payloadMap.put("timestamp", now / 1000.0);

        String jsonPayload = gson.toJson(payloadMap);

        // Run HTTP request asynchronously off main server tick thread
        Bukkit.getScheduler().runTaskAsynchronously(this, () -> sendTelemetry(jsonPayload));
    }

    private void sendTelemetry(String jsonPayload) {
        try {
            URL url = URI.create(BACKEND_URL).toURL();
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestProperty("Accept", "application/json");
            conn.setDoOutput(true);
            conn.setConnectTimeout(3000);
            conn.setReadTimeout(3000);

            byte[] input = jsonPayload.getBytes(StandardCharsets.UTF_8);
            try (OutputStream os = conn.getOutputStream()) {
                os.write(input, 0, input.length);
                os.flush();
            }

            int responseCode = conn.getResponseCode();
            if (responseCode != 200) {
                try (InputStream es = conn.getErrorStream()) {
                    String errorResp = es != null ? new String(es.readAllBytes(), StandardCharsets.UTF_8) : "";
                    getLogger().warning("Telemetry status " + responseCode + " | Response: " + errorResp);
                }
            }
            conn.disconnect();
        } catch (Exception e) {
            getLogger().severe("Failed to send telemetry: " + e.getMessage());
        }
    }

    @Override
    public void onDisable() {
        getLogger().info("Pixel Park Core shutting down.");
    }
}