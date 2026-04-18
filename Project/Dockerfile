FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY pnpm-lock.yaml ./

# Install dependencies using npm (or pnpm if desired, falling back to npm ci)
RUN npm i --legacy-peer-deps

COPY . .

# Build step if production, but we can just run dev server for ease of use in this setup
# RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
