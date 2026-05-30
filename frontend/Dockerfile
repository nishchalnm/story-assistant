FROM node:20-alpine
WORKDIR /app
RUN npm install -g create-next-app@14
RUN npx create-next-app@14 . --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*" --yes
CMD ["npm", "run", "dev"]
