import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { logger } from '../utils/logger';
import { configManager } from '../utils/config';
import axios from 'axios';

interface IntegrationOptions {
  config?: string;
  dryRun?: boolean;
}

export async function integrateCommand(
  services: string[],
  options: IntegrationOptions = {}
): Promise<void> {
  try {
    logger.step('Setting up integrations with external services');

    // Validate services
    const validServices = ['supabase', 'stripe', 'auth0', 'sendgrid', 'aws', 'vercel', 'netlify'];
    const invalidServices = services.filter(service => !validServices.includes(service));
    
    if (invalidServices.length > 0) {
      logger.error(`Invalid services: ${invalidServices.join(', ')}`);
      logger.info(`Valid services: ${validServices.join(', ')}`);
      process.exit(1);
    }

    logger.info(`Integrating with: ${services.join(', ')}`);

    // Load configuration if provided
    let config = {};
    if (options.config && await fs.pathExists(options.config)) {
      config = await fs.readJson(options.config);
    }

    // Setup each service
    const integrationResults: IntegrationResult[] = [];

    for (const service of services) {
      try {
        const result = await setupService(service, config, options.dryRun);
        integrationResults.push(result);
      } catch (error) {
        logger.warn(`Failed to setup ${service}: ${error}`);
        integrationResults.push({
          service,
          success: false,
          error: error.message,
          files: [],
          dependencies: []
        });
      }
    }

    // Display results
    displayIntegrationResults(integrationResults);

    // Save configuration
    if (!options.dryRun) {
      await saveIntegrationConfig(integrationResults);
    }

    logger.success('Integration setup complete!');

  } catch (error) {
    logger.error('Failed to setup integrations:', error);
    process.exit(1);
  }
}

interface IntegrationResult {
  service: string;
  success: boolean;
  error?: string;
  files: string[];
  dependencies: string[];
  config?: Record<string, any>;
}

async function setupService(service: string, config: any, dryRun: boolean): Promise<IntegrationResult> {
  const spinner = ora(`Setting up ${service}...`).start();
  
  try {
    let result: IntegrationResult;
    
    switch (service) {
      case 'supabase':
        result = await setupSupabase(config, dryRun);
        break;
      case 'stripe':
        result = await setupStripe(config, dryRun);
        break;
      case 'auth0':
        result = await setupAuth0(config, dryRun);
        break;
      case 'sendgrid':
        result = await setupSendGrid(config, dryRun);
        break;
      case 'aws':
        result = await setupAWS(config, dryRun);
        break;
      case 'vercel':
        result = await setupVercel(config, dryRun);
        break;
      case 'netlify':
        result = await setupNetlify(config, dryRun);
        break;
      default:
        throw new Error(`Unknown service: ${service}`);
    }
    
    if (result.success) {
      spinner.succeed(`${service} setup complete`);
    } else {
      spinner.fail(`${service} setup failed`);
    }
    
    return result;
    
  } catch (error) {
    spinner.fail(`${service} setup failed`);
    throw error;
  }
}

async function setupSupabase(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = ['@supabase/supabase-js'];
  
  if (!dryRun) {
    // Create Supabase client
    const supabaseClient = `import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types (generate with: npx supabase gen types typescript)
export interface Database {
  // Add your database types here
}`;
    
    await fs.writeFile('lib/supabase.ts', supabaseClient);
    files.push('lib/supabase.ts');
    
    // Create environment variables template
    const envExample = `# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key`;
    
    await fs.appendFile('.env.example', envExample);
    files.push('.env.example');
  }
  
  return {
    service: 'supabase',
    success: true,
    files,
    dependencies,
    config: {
      url: config.supabase?.url || 'your_supabase_url',
      anonKey: config.supabase?.anonKey || 'your_supabase_anon_key'
    }
  };
}

async function setupStripe(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = ['stripe', '@stripe/stripe-js'];
  
  if (!dryRun) {
    // Create Stripe client
    const stripeClient = `import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export const getStripe = () => {
  if (typeof window !== 'undefined') {
    return require('@stripe/stripe-js').loadStripe(
      process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
    );
  }
  return null;
};`;
    
    await fs.writeFile('lib/stripe.ts', stripeClient);
    files.push('lib/stripe.ts');
    
    // Create payment API route
    const paymentRoute = `import { NextApiRequest, NextApiResponse } from 'next';
import { stripe } from '../../../lib/stripe';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { amount, currency = 'usd' } = req.body;
      
      const paymentIntent = await stripe.paymentIntents.create({
        amount: amount * 100, // Convert to cents
        currency,
      });
      
      res.status(200).json({ clientSecret: paymentIntent.client_secret });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end('Method Not Allowed');
  }
}`;
    
    await fs.ensureDir('pages/api/payments');
    await fs.writeFile('pages/api/payments/create-payment-intent.ts', paymentRoute);
    files.push('pages/api/payments/create-payment-intent.ts');
    
    // Update environment variables
    const envExample = `# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret`;
    
    await fs.appendFile('.env.example', envExample);
    files.push('.env.example');
  }
  
  return {
    service: 'stripe',
    success: true,
    files,
    dependencies,
    config: {
      secretKey: config.stripe?.secretKey || 'your_stripe_secret_key',
      publishableKey: config.stripe?.publishableKey || 'your_stripe_publishable_key'
    }
  };
}

async function setupAuth0(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = ['@auth0/nextjs-auth0'];
  
  if (!dryRun) {
    // Create Auth0 configuration
    const auth0Config = `import { initAuth0 } from '@auth0/nextjs-auth0';

export default initAuth0({
  secret: process.env.AUTH0_SECRET,
  issuerBaseURL: process.env.AUTH0_ISSUER_BASE_URL,
  baseURL: process.env.AUTH0_BASE_URL,
  clientID: process.env.AUTH0_CLIENT_ID,
  clientSecret: process.env.AUTH0_CLIENT_SECRET,
});`;
    
    await fs.writeFile('lib/auth0.ts', auth0Config);
    files.push('lib/auth0.ts');
    
    // Create API route
    const apiRoute = `import { handleAuth, handleLogin, handleLogout, handleCallback } from '@auth0/nextjs-auth0';

export default handleAuth({
  login: handleLogin({
    returnTo: '/dashboard'
  }),
  logout: handleLogout({
    returnTo: '/'
  }),
  callback: handleCallback()
});`;
    
    await fs.ensureDir('pages/api/auth');
    await fs.writeFile('pages/api/auth/[...auth0].ts', apiRoute);
    files.push('pages/api/auth/[...auth0].ts');
    
    // Update environment variables
    const envExample = `# Auth0
AUTH0_SECRET=your_auth0_secret
AUTH0_ISSUER_BASE_URL=https://your-domain.auth0.com
AUTH0_BASE_URL=http://localhost:3000
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret`;
    
    await fs.appendFile('.env.example', envExample);
    files.push('.env.example');
  }
  
  return {
    service: 'auth0',
    success: true,
    files,
    dependencies,
    config: {
      domain: config.auth0?.domain || 'your-domain.auth0.com',
      clientId: config.auth0?.clientId || 'your_client_id',
      clientSecret: config.auth0?.clientSecret || 'your_client_secret'
    }
  };
}

async function setupSendGrid(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = ['@sendgrid/mail'];
  
  if (!dryRun) {
    // Create SendGrid client
    const sendgridClient = `import sgMail from '@sendgrid/mail';

sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

export const sendEmail = async (to: string, subject: string, html: string) => {
  const msg = {
    to,
    from: process.env.SENDGRID_FROM_EMAIL!,
    subject,
    html,
  };
  
  try {
    await sgMail.send(msg);
    return { success: true };
  } catch (error) {
    console.error('SendGrid error:', error);
    return { success: false, error: error.message };
  }
};`;
    
    await fs.writeFile('lib/sendgrid.ts', sendgridClient);
    files.push('lib/sendgrid.ts');
    
    // Update environment variables
    const envExample = `# SendGrid
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_email@example.com`;
    
    await fs.appendFile('.env.example', envExample);
    files.push('.env.example');
  }
  
  return {
    service: 'sendgrid',
    success: true,
    files,
    dependencies,
    config: {
      apiKey: config.sendgrid?.apiKey || 'your_sendgrid_api_key',
      fromEmail: config.sendgrid?.fromEmail || 'your_verified_email@example.com'
    }
  };
}

async function setupAWS(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = ['aws-sdk'];
  
  if (!dryRun) {
    // Create AWS configuration
    const awsConfig = `import AWS from 'aws-sdk';

// Configure AWS
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION || 'us-east-1'
});

export const s3 = new AWS.S3();
export const dynamodb = new AWS.DynamoDB.DocumentClient();
export const lambda = new AWS.Lambda();`;
    
    await fs.writeFile('lib/aws.ts', awsConfig);
    files.push('lib/aws.ts');
    
    // Update environment variables
    const envExample = `# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1`;
    
    await fs.appendFile('.env.example', envExample);
    files.push('.env.example');
  }
  
  return {
    service: 'aws',
    success: true,
    files,
    dependencies,
    config: {
      accessKeyId: config.aws?.accessKeyId || 'your_access_key',
      secretAccessKey: config.aws?.secretAccessKey || 'your_secret_key',
      region: config.aws?.region || 'us-east-1'
    }
  };
}

async function setupVercel(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = [];
  
  if (!dryRun) {
    // Create Vercel configuration
    const vercelConfig = `{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}`;
    
    await fs.writeFile('vercel.json', vercelConfig);
    files.push('vercel.json');
  }
  
  return {
    service: 'vercel',
    success: true,
    files,
    dependencies,
    config: {}
  };
}

async function setupNetlify(config: any, dryRun: boolean): Promise<IntegrationResult> {
  const files: string[] = [];
  const dependencies: string[] = [];
  
  if (!dryRun) {
    // Create Netlify configuration
    const netlifyConfig = `[build]
  publish = "out"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200`;
    
    await fs.writeFile('netlify.toml', netlifyConfig);
    files.push('netlify.toml');
  }
  
  return {
    service: 'netlify',
    success: true,
    files,
    dependencies,
    config: {}
  };
}

function displayIntegrationResults(results: IntegrationResult[]): void {
  console.log(chalk.bold('\n🔗 Integration Results\n'));
  
  for (const result of results) {
    const status = result.success ? chalk.green('✓') : chalk.red('✗');
    console.log(`${status} ${chalk.bold(result.service)}`);
    
    if (result.success) {
      if (result.files.length > 0) {
        console.log(`  ${chalk.blue('Files created:')}`);
        result.files.forEach(file => console.log(`    - ${file}`));
      }
      
      if (result.dependencies.length > 0) {
        console.log(`  ${chalk.yellow('Dependencies to install:')}`);
        result.dependencies.forEach(dep => console.log(`    - ${dep}`));
      }
    } else {
      console.log(`  ${chalk.red('Error:')} ${result.error}`);
    }
    
    console.log('');
  }
  
  // Summary
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(chalk.bold('📊 Summary:'));
  console.log(`  Successful: ${successful}`);
  console.log(`  Failed: ${failed}`);
  
  if (successful > 0) {
    console.log(chalk.green('\n🎉 Integration setup complete!'));
    console.log(chalk.gray('Remember to:'));
    console.log(chalk.gray('  1. Install dependencies: npm install'));
    console.log(chalk.gray('  2. Set up environment variables'));
    console.log(chalk.gray('  3. Configure service accounts'));
  }
}

async function saveIntegrationConfig(results: IntegrationResult[]): Promise<void> {
  const config = {
    integrations: results.reduce((acc, result) => {
      if (result.success) {
        acc[result.service] = {
          enabled: true,
          config: result.config || {},
          files: result.files,
          dependencies: result.dependencies
        };
      }
      return acc;
    }, {} as Record<string, any>),
    lastUpdated: new Date().toISOString()
  };
  
  await fs.writeFile('.coding-agent-integrations.json', JSON.stringify(config, null, 2));
  logger.info('Integration configuration saved to .coding-agent-integrations.json');
}
