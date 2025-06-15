#!/usr/bin/env node

/**
 * にじさんじ非公式wikiからライバー情報を取得するMCPサーバー
 * 機能:
 * - ライバー一覧の取得
 * - 個別ライバーの詳細情報取得
 * - カテゴリ別ライバー検索
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import axios from 'axios';
import * as cheerio from 'cheerio';

interface VtuberInfo {
  name: string;
  debut_date?: string;
  gender?: string;
  voice_type?: string;
  personality_traits: string[];
  streaming_genres: string[];
  game_genres: string[];
  main_streaming_time?: string;
  subscriber_count?: number;
  avatar_color_theme?: string;
  description?: string;
  wiki_url?: string;
}

/**
 * にじさんじwikiからライバー情報を取得するクラス
 */
class NijisanjiWikiScraper {
  private baseUrl = 'https://wikiwiki.jp/nijisanji';
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
  }

  /**
   * ライバー一覧ページを取得
   */
  async getVtuberList(): Promise<string[]> {
    try {
      // メインページからライバー名を取得
      const response = await this.axiosInstance.get(`${this.baseUrl}/`);
      const $ = cheerio.load(response.data);
      
      const vtubers: string[] = [];
      
      // メインページからライバー名のリンクを抽出
      $('a[href*="/nijisanji/"]').each((i, element) => {
        const href = $(element).attr('href');
        const text = $(element).text().trim();
        
        if (href && text && !href.includes('::') && text.length > 0 && text.length < 30) {
          // 日本語の名前っぽいものを抽出
          if (/^[ひらがなカタカナ漢字・ー\w\s]+$/.test(text)) {
            const decodedName = decodeURIComponent(text);
            if (!vtubers.includes(decodedName) && 
                !['ホーム', '新規', '編集', '添付', '一覧', '最終更新', '差分', 'バックアップ', '凍結', '複製', '名前変更', 'ヘルプ'].includes(decodedName)) {
              vtubers.push(decodedName);
            }
          }
        }
      });

      // ページ一覧からも追加で取得
      try {
        const listResponse = await this.axiosInstance.get(`${this.baseUrl}/::cmd/list`);
        const $list = cheerio.load(listResponse.data);
        
        $list('a').each((i, element) => {
          const href = $list(element).attr('href');
          const text = $list(element).text().trim();
          
          if (href && href.includes('/nijisanji/') && text.length > 0 && text.length < 30) {
            // 日本語の名前っぽいものを抽出
            if (/^[ひらがなカタカナ漢字・ー\w\s]+$/.test(text) && !text.includes('::')) {
              const decodedName = decodeURIComponent(text);
              if (!vtubers.includes(decodedName) && 
                  !['FrontPage', 'MenuBar', 'SandBox', 'FAQ', 'Glossary'].includes(decodedName)) {
                vtubers.push(decodedName);
              }
            }
          }
        });
      } catch (listError) {
        console.error('Error fetching page list:', listError);
      }

      return vtubers.filter(name => name.length > 0).slice(0, 200); // 最大200名
    } catch (error) {
      console.error('Error fetching vtuber list:', error);
      return [];
    }
  }

  /**
   * 個別ライバーの詳細情報を取得
   */
  async getVtuberDetails(name: string): Promise<VtuberInfo | null> {
    try {
      const encodedName = encodeURIComponent(name);
      const response = await this.axiosInstance.get(`${this.baseUrl}/${encodedName}`);
      const $ = cheerio.load(response.data);
      
      const vtuber: VtuberInfo = {
        name: name,
        personality_traits: [],
        streaming_genres: [],
        game_genres: [],
        wiki_url: `${this.baseUrl}/${encodedName}`
      };

      // 基本情報テーブルから情報を抽出
      $('table tr').each((i, row) => {
        const cells = $(row).find('td');
        if (cells.length >= 2) {
          const key = $(cells[0]).text().trim();
          const value = $(cells[1]).text().trim();

          switch (key) {
            case '初配信日':
            case 'デビュー日':
              if (value.match(/\d{4}[年/\-]\d{1,2}[月/\-]\d{1,2}/)) {
                vtuber.debut_date = this.parseDate(value);
              }
              break;
            case '性別':
              if (value.includes('女') || value.includes('♀')) {
                vtuber.gender = '女性';
              } else if (value.includes('男') || value.includes('♂')) {
                vtuber.gender = '男性';
              }
              break;
          }
        }
      });

      // 本文から特徴を抽出
      const bodyText = $('body').text();
      
      // 配信ジャンルを推定
      const streamingGenres = [];
      if (bodyText.includes('雑談') || bodyText.includes('フリートーク')) streamingGenres.push('雑談');
      if (bodyText.includes('ゲーム')) streamingGenres.push('ゲーム');
      if (bodyText.includes('歌') || bodyText.includes('歌唱') || bodyText.includes('歌枠')) streamingGenres.push('歌');
      if (bodyText.includes('ASMR')) streamingGenres.push('ASMR');
      if (bodyText.includes('お絵描き') || bodyText.includes('絵')) streamingGenres.push('お絵描き');
      if (bodyText.includes('企画')) streamingGenres.push('企画');
      
      vtuber.streaming_genres = streamingGenres;

      // ゲームジャンルを推定
      const gameGenres = [];
      if (bodyText.includes('FPS') || bodyText.includes('Apex') || bodyText.includes('VALORANT')) gameGenres.push('FPS');
      if (bodyText.includes('RPG') || bodyText.includes('ロールプレイング')) gameGenres.push('RPG');
      if (bodyText.includes('アクション')) gameGenres.push('アクション');
      if (bodyText.includes('パズル')) gameGenres.push('パズル');
      if (bodyText.includes('シミュレーション')) gameGenres.push('シミュレーション');
      if (bodyText.includes('格闘') || bodyText.includes('ファイティング')) gameGenres.push('格闘');
      if (bodyText.includes('ホラー')) gameGenres.push('ホラー');
      if (bodyText.includes('音ゲー') || bodyText.includes('リズムゲーム')) gameGenres.push('音ゲー');
      
      vtuber.game_genres = gameGenres;

      // 性格特性を推定
      const personalityTraits = [];
      if (bodyText.includes('元気') || bodyText.includes('明るい')) personalityTraits.push('元気');
      if (bodyText.includes('おっとり') || bodyText.includes('のんびり')) personalityTraits.push('おっとり');
      if (bodyText.includes('優しい') || bodyText.includes('癒し')) personalityTraits.push('優しい');
      if (bodyText.includes('クール') || bodyText.includes('冷静')) personalityTraits.push('クール');
      if (bodyText.includes('面白い') || bodyText.includes('ユニーク')) personalityTraits.push('面白い');
      if (bodyText.includes('知的') || bodyText.includes('頭がいい')) personalityTraits.push('知的');
      
      vtuber.personality_traits = personalityTraits;

      // 登録者数を抽出（もしあれば）
      const subscriberMatch = bodyText.match(/登録者[数\s]*[：:]?\s*([0-9,]+)/);
      if (subscriberMatch) {
        vtuber.subscriber_count = parseInt(subscriberMatch[1].replace(/,/g, ''));
      }

      // 説明文を抽出
      const description = $('p').first().text().trim();
      if (description.length > 0 && description.length < 500) {
        vtuber.description = description;
      }

      return vtuber;
    } catch (error) {
      console.error(`Error fetching details for ${name}:`, error);
      return null;
    }
  }

  /**
   * 日付文字列をISO形式に変換
   */
  private parseDate(dateStr: string): string {
    const match = dateStr.match(/(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})/);
    if (match) {
      const year = match[1];
      const month = match[2].padStart(2, '0');
      const day = match[3].padStart(2, '0');
      return `${year}-${month}-${day}`;
    }
    return dateStr;
  }
}

/**
 * MCPサーバーの設定
 */
const server = new Server(
  {
    name: "nijisanji-wiki-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
    },
  }
);

const scraper = new NijisanjiWikiScraper();

/**
 * 利用可能なツールの一覧を返す
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_vtuber_list",
        description: "にじさんじライバーの一覧を取得する",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "get_vtuber_details",
        description: "指定されたライバーの詳細情報を取得する",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "ライバー名"
            }
          },
          required: ["name"]
        }
      },
      {
        name: "get_multiple_vtuber_details",
        description: "複数のライバーの詳細情報を一括取得する",
        inputSchema: {
          type: "object",
          properties: {
            names: {
              type: "array",
              items: {
                type: "string"
              },
              description: "ライバー名の配列"
            },
            limit: {
              type: "number",
              description: "取得する最大数（デフォルト: 20）",
              minimum: 1,
              maximum: 50
            }
          },
          required: ["names"]
        }
      }
    ]
  };
});

/**
 * ツールの実行ハンドラー
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "get_vtuber_list": {
        const vtubers = await scraper.getVtuberList();
        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              count: vtubers.length,
              vtubers: vtubers
            }, null, 2)
          }]
        };
      }

      case "get_vtuber_details": {
        const name = String(request.params.arguments?.name);
        if (!name) {
          throw new McpError(ErrorCode.InvalidParams, "ライバー名が必要です");
        }

        const details = await scraper.getVtuberDetails(name);
        if (!details) {
          return {
            content: [{
              type: "text",
              text: `ライバー「${name}」の情報が見つかりませんでした。`
            }],
            isError: true
          };
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify(details, null, 2)
          }]
        };
      }

      case "get_multiple_vtuber_details": {
        const names = request.params.arguments?.names as string[];
        const limit = Math.min(Number(request.params.arguments?.limit) || 20, 50);
        
        if (!Array.isArray(names)) {
          throw new McpError(ErrorCode.InvalidParams, "ライバー名の配列が必要です");
        }

        const results: VtuberInfo[] = [];
        const processNames = names.slice(0, limit);

        for (const name of processNames) {
          try {
            const details = await scraper.getVtuberDetails(name);
            if (details) {
              results.push(details);
            }
            // レート制限を避けるために少し待機
            await new Promise(resolve => setTimeout(resolve, 500));
          } catch (error) {
            console.error(`Error processing ${name}:`, error);
          }
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              processed: processNames.length,
              successful: results.length,
              vtubers: results
            }, null, 2)
          }]
        };
      }

      default:
        throw new McpError(ErrorCode.MethodNotFound, `未知のツール: ${request.params.name}`);
    }
  } catch (error) {
    if (error instanceof McpError) {
      throw error;
    }
    throw new McpError(ErrorCode.InternalError, `ツール実行エラー: ${error}`);
  }
});

/**
 * サーバーを開始
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("にじさんじwiki MCPサーバーが起動しました");
}

main().catch((error) => {
  console.error("サーバーエラー:", error);
  process.exit(1);
});
