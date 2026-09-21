End-to-end startup guide to get everything running in order.

## 1. Start Docker Desktop
Open Docker Desktop from Start menu and wait until status icon in the bottom-left corner turns green.

## 2. Compile & Deploy the Java Plugin
In IntelliJ IDEA:
1. Open the Maven sidebar on the right
2. Expand PixelParkCore -> Lifecycle
3. Run clean, then package
4. Copy pixel-park-core-1.0-SNAPSHOT.jar from mc-plugin/target/
5. Paste it into C:\mc-server\plugins\

## 3. Run the Backend API (Terminal 1)
Open PowerShell and execute:    
`cd C:\Users\betzm\IdeaProjects\Pixel-Park\backend          
docker build -t pixel-park-backend .        
docker run -p 8000:8000 pixel-park-backend`     
(Leave this window open to monitor live 200 OK logs)

## 4. Run the Minecraft Server (Terminal 2)
OPen a second PowerShell window and execute:    
`cd C:\mc-server    
& "C:\Users\betzm\.jdks\openjdk-25\bin\java.exe" -Xmx2G -jar server.jar nogui`  

## 5. Launch Minecraft & Test
1. Open Minecraft Launcher and launch snapshot/release 26.1.2
2. Connect to server address localhost
3. Hop into a minecart and ride on the track
4. Check Docker terminal (Terminal 1) to watch incoming telemetry stream in