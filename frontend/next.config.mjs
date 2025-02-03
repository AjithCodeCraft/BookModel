/** @type {import('next').NextConfig} */
const nextConfig = {
    api: {
        bodyParser: {
          sizeLimit: "10mb", // Increase limit to 10MB
        },
      },
    };
    


export default nextConfig;
