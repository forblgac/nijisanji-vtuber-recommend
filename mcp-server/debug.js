import axios from 'axios';
import * as cheerio from 'cheerio';

async function debugWikiStructure() {
  try {
    console.log('にじさんじwikiの構造を確認中...');
    
    // メインページを確認
    const response = await axios.get('https://wikiwiki.jp/nijisanji');
    console.log('Status:', response.status);
    
    const $ = cheerio.load(response.data);
    
    // ページタイトル
    console.log('\nページタイトル:', $('title').text());
    
    // リンクの確認
    console.log('\n主要なリンク:');
    $('a').each((i, element) => {
      if (i < 20) { // 最初の20個だけ
        const href = $(element).attr('href');
        const text = $(element).text().trim();
        if (href && text.length > 0) {
          console.log(`${text} -> ${href}`);
        }
      }
    });

    // ライバー一覧ページを直接確認
    console.log('\n\nライバー一覧ページを確認中...');
    try {
      const listResponse = await axios.get('https://wikiwiki.jp/nijisanji/ライバー一覧');
      const $list = cheerio.load(listResponse.data);
      console.log('ライバー一覧ページタイトル:', $list('title').text());
      
      // ライバー名と思われるリンクを探す
      console.log('\nライバー名候補:');
      $list('a').each((i, element) => {
        const href = $list(element).attr('href');
        const text = $list(element).text().trim();
        
        if (href && text && text.length > 0 && text.length < 20) {
          // にじさんじのライバー名っぽいものを抽出
          if (href.includes('nijisanji') && !href.includes('ライバー一覧') && !href.includes('#')) {
            console.log(`${text} -> ${href}`);
          }
        }
      });
      
    } catch (listError) {
      console.error('ライバー一覧ページエラー:', listError.message);
    }
    
  } catch (error) {
    console.error('エラー:', error.message);
  }
}

debugWikiStructure();
