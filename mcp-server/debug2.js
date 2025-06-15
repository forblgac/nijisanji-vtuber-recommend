import axios from 'axios';
import * as cheerio from 'cheerio';

async function exploreWikiStructure() {
  try {
    console.log('メインページの詳細を確認中...');
    
    const response = await axios.get('https://wikiwiki.jp/nijisanji/');
    const $ = cheerio.load(response.data);
    
    console.log('\nページ内容の概要:');
    
    // すべてのリンクを詳しく確認
    console.log('\nすべてのリンク（nijisanjiを含む）:');
    const links = [];
    $('a').each((i, element) => {
      const href = $(element).attr('href');
      const text = $(element).text().trim();
      
      if (href && href.includes('nijisanji') && text.length > 0) {
        links.push({ text, href });
      }
    });
    
    // 重複を除去して表示
    const uniqueLinks = links.filter((link, index, self) => 
      index === self.findIndex((t) => t.href === link.href)
    ).slice(0, 50);
    
    uniqueLinks.forEach(link => {
      console.log(`${link.text} -> ${link.href}`);
    });
    
    // ページ一覧を取得してみる
    console.log('\n\nページ一覧を確認中...');
    try {
      const listResponse = await axios.get('https://wikiwiki.jp/nijisanji/::cmd/list');
      const $list = cheerio.load(listResponse.data);
      console.log('ページ一覧タイトル:', $list('title').text());
      
      // ライバー名と思われるページを探す
      $list('a').each((i, element) => {
        const href = $list(element).attr('href');
        const text = $list(element).text().trim();
        
        if (href && href.includes('/nijisanji/') && text.length > 0 && text.length < 30) {
          // 日本語の名前っぽいものを抽出
          if (/^[ひらがなカタカナ漢字・ー\w\s]+$/.test(text) && !text.includes('::')) {
            console.log(`候補: ${text} -> ${href}`);
          }
        }
      });
      
    } catch (listError) {
      console.error('ページ一覧エラー:', listError.message);
    }
    
  } catch (error) {
    console.error('エラー:', error.message);
  }
}

exploreWikiStructure();
