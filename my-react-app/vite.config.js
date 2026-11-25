/*
 * @Author: along
 * @Description: 
 * @Date: 2026-10-26 11:56:24
 * @LastEditors: along
 * @LastEditTime: 2026-11-24 16:44:06
 * @FilePath: /my-react-app/vite.config.js
 */
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import svgr from 'vite-plugin-svgr';
import compression from 'vite-plugin-compression'
import { VitePWA } from 'vite-plugin-pwa'
import checker from 'vite-plugin-checker'
import { fileURLToPath } from 'node:url';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // SVG作为组件导入
    svgr(),
    
    // Gzip压缩
    compression({
      algorithm: 'gzip',
      ext: '.gz'
    }),
    
    // PWA
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'My React App',
        short_name: 'ReactApp',
        theme_color: '#ffffff'
      }
    }),
    
    // JavaScript / JSX代码检查
    checker({
      eslint: {
        lintCommand: 'eslint "./src/**/*.{js,jsx}"'
      }
    })
  ],

  // 开发服务器配置
  server: {
    port: 3000, // 端口号
    open: true, // 自动打开浏览器
    host: true, // 监听所有地址
    cors: true, // 启用CORS
    proxy: {
      // 代理配置
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },

  // 构建配置
  build: {
    outDir: 'dist', // 输出目录
    sourcemap: false, // 是否生成sourcemap
    minify: 'terser', // 压缩方式
    chunkSizeWarningLimit: 1000, // chunk大小警告限制
    rollupOptions: {
      output: {
        // 分包策略
        manualChunks(id) {
          if (id.includes('/node_modules/react/') || id.includes('/node_modules/react-dom/')) {
            return 'vendor';
          }
          if (id.includes('/node_modules/react-router-dom/')) {
            return 'router';
          }
        },
      },
    },
  },

  // 路径别名
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@utils': fileURLToPath(new URL('./src/utils', import.meta.url)),
    },
  },

  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
    modules: {
      localsConvention: 'camelCase', // CSS模块命名转换
    },
  },
});
