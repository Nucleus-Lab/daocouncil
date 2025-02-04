import { PrivyClient } from '@privy-io/react-auth';

export const privyClient = new PrivyClient({
    appId: import.meta.env.VITE_PRIVY_APP_ID,
    loginMethods: ['wallet'],  // 
    appearance: {
        theme: 'light',
        accentColor: '#676FFF',
    },
});
