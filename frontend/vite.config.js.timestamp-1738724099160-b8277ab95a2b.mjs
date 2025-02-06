// vite.config.js
import { defineConfig } from "file:///mnt/c/Users/jhcho/OneDrive%20-%20%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6/Desktop/Nucleus_Lab/ai_hackathon/daocouncil/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///mnt/c/Users/jhcho/OneDrive%20-%20%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6/Desktop/Nucleus_Lab/ai_hackathon/daocouncil/frontend/node_modules/@vitejs/plugin-react/dist/index.mjs";
var vite_config_default = defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true
    },
    hmr: {
      overlay: true
    }
  },
  resolve: {
    alias: {
      process: "process/browser",
      stream: "stream-browserify",
      util: "util"
    }
  },
  define: {
    "process.env": {},
    global: {}
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvbW50L2MvVXNlcnMvamhjaG8vT25lRHJpdmUgLSBcdTUzMTdcdTRFQUNcdTU5MjdcdTVCNjYvRGVza3RvcC9OdWNsZXVzX0xhYi9haV9oYWNrYXRob24vZGFvY291bmNpbC9mcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL21udC9jL1VzZXJzL2poY2hvL09uZURyaXZlIC0gXHU1MzE3XHU0RUFDXHU1OTI3XHU1QjY2L0Rlc2t0b3AvTnVjbGV1c19MYWIvYWlfaGFja2F0aG9uL2Rhb2NvdW5jaWwvZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL21udC9jL1VzZXJzL2poY2hvL09uZURyaXZlJTIwLSUyMCVFNSU4QyU5NyVFNCVCQSVBQyVFNSVBNCVBNyVFNSVBRCVBNi9EZXNrdG9wL051Y2xldXNfTGFiL2FpX2hhY2thdGhvbi9kYW9jb3VuY2lsL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCByZWFjdCBmcm9tICdAdml0ZWpzL3BsdWdpbi1yZWFjdCdcblxuLy8gaHR0cHM6Ly92aXRlanMuZGV2L2NvbmZpZy9cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFtyZWFjdCgpXSxcbiAgc2VydmVyOiB7XG4gICAgd2F0Y2g6IHtcbiAgICAgIHVzZVBvbGxpbmc6IHRydWUsXG4gICAgfSxcbiAgICBobXI6IHtcbiAgICAgIG92ZXJsYXk6IHRydWVcbiAgICB9XG4gIH0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgcHJvY2VzczogXCJwcm9jZXNzL2Jyb3dzZXJcIixcbiAgICAgIHN0cmVhbTogXCJzdHJlYW0tYnJvd3NlcmlmeVwiLFxuICAgICAgdXRpbDogXCJ1dGlsXCJcbiAgICB9XG4gIH0sXG4gIGRlZmluZToge1xuICAgICdwcm9jZXNzLmVudic6IHt9LFxuICAgIGdsb2JhbDoge31cbiAgfVxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBMmQsU0FBUyxvQkFBb0I7QUFDeGYsT0FBTyxXQUFXO0FBR2xCLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVMsQ0FBQyxNQUFNLENBQUM7QUFBQSxFQUNqQixRQUFRO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxZQUFZO0FBQUEsSUFDZDtBQUFBLElBQ0EsS0FBSztBQUFBLE1BQ0gsU0FBUztBQUFBLElBQ1g7QUFBQSxFQUNGO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxTQUFTO0FBQUEsTUFDVCxRQUFRO0FBQUEsTUFDUixNQUFNO0FBQUEsSUFDUjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLGVBQWUsQ0FBQztBQUFBLElBQ2hCLFFBQVEsQ0FBQztBQUFBLEVBQ1g7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
