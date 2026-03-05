/**
 * SSH Remote Control Panel - Server
 * Web-based SSH terminal with multi-server management
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { Client } = require('ssh2');
const session = require('express-session');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

// Session middleware
app.use(session({
  secret: process.env.SESSION_SECRET || 'ssh-panel-secret-key-change-in-production',
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false, maxAge: 3600000 }
}));

// Static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Server configurations storage (in-memory for now, can be persisted)
const serverConfigs = new Map();
const activeConnections = new Map();

// API Routes

// Get all saved servers
app.get('/api/servers', (req, res) => {
  const servers = Array.from(serverConfigs.entries()).map(([id, config]) => ({
    id,
    name: config.name,
    host: config.host,
    port: config.port,
    username: config.username,
    connected: activeConnections.has(id)
  }));
  res.json({ success: true, servers });
});

// Add a new server
app.post('/api/servers', (req, res) => {
  const { name, host, port = 22, username, password, privateKey, passphrase } = req.body;
  
  console.log(`[API] Saving server: ${username}@${host}:${port}, hasPassword=${!!password}, hasKey=${!!privateKey}`);
  
  if (!host || !username) {
    return res.status(400).json({ success: false, error: 'Host and username are required' });
  }

  const id = `${username}@${host}:${port}`;
  
  serverConfigs.set(id, {
    name: name || id,
    host,
    port,
    username,
    password,
    privateKey,
    passphrase
  });

  res.json({ success: true, id, message: 'Server saved' });
});

// Delete a server
app.delete('/api/servers/:id', (req, res) => {
  const { id } = req.params;
  
  // Disconnect if connected
  if (activeConnections.has(id)) {
    const conn = activeConnections.get(id);
    conn.end();
    activeConnections.delete(id);
  }
  
  serverConfigs.delete(id);
  res.json({ success: true, message: 'Server deleted' });
});

// Webpage route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Socket.IO handling for SSH connections
io.on('connection', (socket) => {
  console.log(`[Socket] Client connected: ${socket.id}`);
  
  let currentStream = null;
  let currentConn = null;

  // Connect to SSH server
  socket.on('ssh:connect', (config) => {
    let { id, host, port = 22, username, password, privateKey, passphrase } = config;
    
    // If id provided, get full config from serverConfigs (includes credentials)
    if (id && serverConfigs.has(id)) {
      const savedConfig = serverConfigs.get(id);
      host = savedConfig.host;
      port = savedConfig.port;
      username = savedConfig.username;
      password = savedConfig.password;
      privateKey = savedConfig.privateKey;
      passphrase = savedConfig.passphrase;
      console.log(`[SSH] Using saved config for ${id}, hasPassword=${!!password}, hasKey=${!!privateKey}`);
    }
    
    console.log(`[SSH] Connecting to ${username}@${host}:${port}, auth=${password ? 'password' : (privateKey ? 'key' : 'none')}`);
    
    if (!host || !username) {
      socket.emit('ssh:error', { message: 'Host and username are required' });
      return;
    }

    if (!password && !privateKey) {
      socket.emit('ssh:error', { message: 'Password or private key is required' });
      return;
    }

    const conn = new Client();
    
    const connConfig = {
      host,
      port: parseInt(port),
      username,
      readyTimeout: 30000
    };

    if (password) {
      connConfig.password = password;
    } else if (privateKey) {
      connConfig.privateKey = privateKey;
      if (passphrase) connConfig.passphrase = passphrase;
    }

    conn.on('ready', () => {
      console.log(`[SSH] Connected to ${username}@${host}:${port}`);
      
      const serverId = id || `${username}@${host}:${port}`;
      activeConnections.set(serverId, conn);
      
      socket.emit('ssh:connected', { 
        id: serverId,
        host,
        port,
        username 
      });

      // Start shell
      conn.shell((err, stream) => {
        if (err) {
          socket.emit('ssh:error', { message: `Shell error: ${err.message}` });
          return;
        }

        currentStream = stream;
        currentConn = conn;

        stream.on('data', (data) => {
          socket.emit('ssh:data', { data: data.toString('base64') });
        });

        stream.on('close', () => {
          socket.emit('ssh:disconnected', { message: 'Shell closed' });
          conn.end();
          if (id) activeConnections.delete(id);
        });

        stream.stderr.on('data', (data) => {
          socket.emit('ssh:data', { data: data.toString('base64'), stderr: true });
        });
      });
    });

    conn.on('error', (err) => {
      console.error(`[SSH] Connection error: ${err.message}`);
      socket.emit('ssh:error', { message: err.message });
    });

    conn.on('close', () => {
      console.log(`[SSH] Connection closed: ${username}@${host}:${port}`);
      socket.emit('ssh:disconnected', { message: 'Connection closed' });
      if (id) activeConnections.delete(id);
    });

    try {
      conn.connect(connConfig);
    } catch (err) {
      socket.emit('ssh:error', { message: `Connection failed: ${err.message}` });
    }
  });

  // Handle terminal input
  socket.on('ssh:data', (data) => {
    if (currentStream && currentStream.writable) {
      currentStream.write(Buffer.from(data.data, 'base64'));
    }
  });

  // Handle terminal resize
  socket.on('ssh:resize', (data) => {
    if (currentStream && currentStream.writable) {
      currentStream.setWindow(data.rows, data.cols, 480, 640);
    }
  });

  // Disconnect
  socket.on('ssh:disconnect', () => {
    if (currentStream) {
      currentStream.end();
      currentStream = null;
    }
    if (currentConn) {
      currentConn.end();
      currentConn = null;
    }
  });

  // Cleanup on socket disconnect
  socket.on('disconnect', () => {
    console.log(`[Socket] Client disconnected: ${socket.id}`);
    if (currentStream) {
      currentStream.end();
    }
    if (currentConn) {
      currentConn.end();
    }
  });
});

// Start server
const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║           SSH Remote Control Panel v1.0.0                  ║
╠════════════════════════════════════════════════════════════╣
║  Web Interface: http://localhost:${PORT}                       ║
║  API Endpoint:  http://localhost:${PORT}/api/servers           ║
╠════════════════════════════════════════════════════════════╣
║  Features:                                                  ║
║  • Multi-server management                                  ║
║  • Web-based terminal (xterm.js)                            ║
║  • Real-time SSH connection                                 ║
║  • Server config persistence                                ║
╚════════════════════════════════════════════════════════════╝
  `);
});